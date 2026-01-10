from typing import TypedDict, Annotated, List, Any, Dict, Optional
import os
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from langchain_aws import ChatBedrock
from langchain_google_genai import ChatGoogleGenerativeAI
from config import Config
from utils.intake import analyze_multimodal_input
from utils.knowledge_base import get_policy_context
from utils.tools import get_part_price, get_labor_rate

# 1. State Definition
class AdjusterState(TypedDict):
    # Inputs
    image_status: str # "clear" or "blurry"
    voice_transcript: str
    
    # Provider Info
    provider: str
    credentials: Dict[str, Any]
    
    # Internal Processing
    intake_result: dict
    policy_context: str
    coverage_verdict: dict
    estimate_details: dict
    
    # Output to UI
    status: str # "processing", "needs_input", "completed", "denied"
    final_message: str

# 2. LLM Helper
def get_llm(provider: str, creds: Dict[str, Any]):
    if provider == "Azure OpenAI":
        return AzureChatOpenAI(
            azure_endpoint=creds.get("azure_endpoint") or Config.AZURE_OPENAI_ENDPOINT,
            api_key=creds.get("azure_key") or Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            deployment_name=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            temperature=0
        )
    elif provider == "AWS Bedrock":
        return ChatBedrock(
            model_id=creds.get("aws_model_id") or "anthropic.claude-v2",
            region_name=creds.get("aws_region") or "us-east-1",
            aws_access_key_id=creds.get("aws_access_key"),
            aws_secret_access_key=creds.get("aws_secret_key"),
            temperature=0
        )
    elif provider == "Google Gemini":
        return ChatGoogleGenerativeAI(
            model=creds.get("google_model") or "gemini-pro",
            google_api_key=creds.get("google_key"),
            temperature=0
        )
    else:
        # Fallback to Azure
        return AzureChatOpenAI(
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            deployment_name=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            temperature=0
        )

# 3. Nodes

def intake_node(state: AdjusterState):
    print("---INTAKE AGENT---")
    result = analyze_multimodal_input(state['image_status'], state['voice_transcript'])
    
    if not result['is_valid']:
        # Cyclic Loop Trigger: Return to user for better input
        return {
            "intake_result": result,
            "status": "needs_input",
            "final_message": result['error_reason']
        }
    
    return {
        "intake_result": result,
        "status": "processing"
    }

def verification_node(state: AdjusterState):
    print("---VERIFICATION AGENT---")
    damage_type = state['intake_result']['damage_detected']
    transcript = state['voice_transcript']
    
    # RAG Retrieval
    query = f"Is {damage_type} covered? Context: {transcript}"
    context = get_policy_context(query)
    
    # LLM Check
    provider = state.get("provider", "Azure OpenAI")
    creds = state.get("credentials", {})
    
    try:
        llm = get_llm(provider, creds)
        prompt = f"""
        You are a Claims Adjuster. Verify coverage based on the policy.
        
        INCIDENT: {transcript}
        DETECTED DAMAGE: {damage_type}
        
        POLICY SECTIONS:
        {context}
        
        Is this incident covered? 
        Return a structured string: "VERDICT: [We Pay | Denied] | REASON:String".
        """
        
        response = llm.invoke([HumanMessage(content=prompt)]).content
        
        verdict_lines = response.split("|")
        is_covered = "We Pay" in response
        reason = verdict_lines[1].replace("REASON:", "").strip() if len(verdict_lines) > 1 else response
        
        return {
            "policy_context": context,
            "coverage_verdict": {
                "is_covered": is_covered,
                "reason": reason
            },
            "status": "processing" if is_covered else "denied",
            "final_message": f"Coverage Verification Complete: {reason}"
        }
    except Exception as e:
        return {
            "status": "denied",
            "final_message": f"Error in Verification Agent: {str(e)}",
            "coverage_verdict": {"is_covered": False, "reason": str(e)}
        }

def estimation_node(state: AdjusterState):
    print("---ESTIMATION AGENT---")
    damage_type = state['intake_result']['damage_detected']
    
    # MCP Tool Calls
    part_price = get_part_price.invoke(damage_type)
    labor_rate = get_labor_rate.invoke("default")
    labor_hours = 2.5 # Simulated logic for this PoC
    
    total = part_price + (labor_rate * labor_hours)
    
    estimate = {
        "part_cost": part_price,
        "labor_cost": labor_rate * labor_hours,
        "total": total,
        "breakdown": f"Part ({damage_type}): ${part_price} | Labor (2.5hrs @ ${labor_rate}/hr): ${labor_rate * labor_hours}"
    }
    
    return {
        "estimate_details": estimate,
        "status": "completed",
        "final_message": f"Claim Settled. Total Payout: ${total:.2f}. Breakdown: {estimate['breakdown']}."
    }

# 4. Edges
def route_after_intake(state: AdjusterState):
    if state['status'] == "needs_input":
        return END
    return "verification_node"

def route_after_verification(state: AdjusterState):
    if not state.get('coverage_verdict', {}).get('is_covered', False):
        return END
    return "estimation_node"

# 5. Graph
workflow = StateGraph(AdjusterState)

workflow.add_node("intake_node", intake_node)
workflow.add_node("verification_node", verification_node)
workflow.add_node("estimation_node", estimation_node)

workflow.set_entry_point("intake_node")

workflow.add_conditional_edges(
    "intake_node",
    route_after_intake,
    {
        END: END,
        "verification_node": "verification_node"
    }
)

workflow.add_conditional_edges(
    "verification_node",
    route_after_verification,
    {
        END: END,
        "estimation_node": "estimation_node"
    }
)

workflow.add_edge("estimation_node", END)

app_graph = workflow.compile()
