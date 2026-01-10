from typing import TypedDict, Annotated, List, Optional, Dict, Any
import os
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from langchain_aws import ChatBedrock
from langchain_google_genai import ChatGoogleGenerativeAI
from config import Config
from utils.data_sources import check_social_media, check_ghost_broking_db, analyze_claim_photo
from utils.guardrails import validate_accusation

# 1. Define State
class AgentState(TypedDict):
    claim_id: str
    claimant_name: str
    claim_date: str
    claim_description: str
    photo_id: str
    
    # Provider Info
    provider: str
    credentials: Dict[str, Any]
    
    evidence_log: List[str]
    fraud_score: float
    risk_reasoning: str
    requires_human_review: bool
    final_decision: str  # "Approved" | "Dismissed" | "Pending"

# 2. Helper to get LLM
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
        # Fallback
        return AzureChatOpenAI(
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            deployment_name=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            temperature=0
        )

# 3. Nodes

def gather_evidence(state: AgentState):
    """
    MCP-style Node: Orchestrates calls to various tools to gather intel.
    """
    print(f"---GATHERING EVIDENCE FOR {state['claim_id']}---")
    evidence = []
    
    # Tool 1: Social Media Check
    social_result = check_social_media.invoke({"name": state['claimant_name'], "claim_date": state['claim_date']})
    evidence.append(f"Social Media Scan: {social_result}")
    
    # Tool 2: Ghost Broking DB
    db_result = check_ghost_broking_db.invoke({"entity_name": state['claimant_name']})
    evidence.append(f"Ghost Broking DB: {db_result}")
    
    # Tool 3: Image Analysis
    img_result = analyze_claim_photo.invoke({"photo_description": state['photo_id']})
    evidence.append(f"Image Analysis: {img_result}")
    
    return {"evidence_log": evidence}

def assess_risk(state: AgentState):
    """
    Synthesizes gathered evidence into a Fraud Score (0-100).
    """
    print("---ASSESSING RISK---")
    
    evidence_text = "\n".join(state['evidence_log'])
    
    system_prompt = (
        "You are a Senior Fraud Investigator AI.\n"
        "Analyze the provided evidence and assign a Fraud Score (0-100).\n"
        "0 = Low Risk, 100 = Confirmed Fraud.\n"
        "Provide a concise reasoning summary.\n"
        "Format output as: Score: <number> | Reason: <text>"
    )
    
    user_prompt = f"""
    Claimant: {state['claimant_name']}
    Claim: {state['claim_description']}
    
    EVIDENCE GATHERED:
    {evidence_text}
    
    Assess the risk. Be objective.
    """
    
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    
    provider = state.get("provider", "Azure OpenAI")
    creds = state.get("credentials", {})
    
    try:
        llm = get_llm(provider, creds)
        response = llm.invoke(messages)
        content = response.content
    except Exception as e:
        content = f"Score: 50 | Reason: LLM Error: {str(e)}"
    
    # Apply Guardrails
    is_safe, refusal_reason = validate_accusation(content)
    if not is_safe:
        score = 50.0 # Default to neutral/review if unsafe
        reason = f"Automated Analysis Blocked by Guardrail: {refusal_reason}"
    else:
        # Simple parsing (robustness would require regex or structured output)
        try:
            parts = content.split(" | Reason: ")
            score_str = parts[0].replace("Score:", "").strip()
            score = float(score_str)
            reason = parts[1].strip()
        except:
            if "Score:" in content: # Try softer parse
                try:
                    import re
                    match = re.search(r"Score:\s*(\d+(\.\d+)?)", content)
                    if match:
                        score = float(match.group(1))
                        reason = content.split("|")[-1].strip() if "|" in content else content
                    else:
                        raise ValueError
                except:
                    score = 50.0
                    reason = "Parsing Error - Manual Review Required. Raw Output: " + content
            else:
                score = 50.0
                reason = "Parsing Error - Manual Review Required. Raw Output: " + content

    requires_review = score > Config.HUMAN_REVIEW_THRESHOLD
    
    return {
        "fraud_score": score,
        "risk_reasoning": reason,
        "requires_human_review": requires_review,
        "final_decision": "Pending" if requires_review else "Approved"
    }

# 4. Graph Construction
workflow = StateGraph(AgentState)

workflow.add_node("investigator", gather_evidence)
workflow.add_node("risk_assessor", assess_risk)

workflow.set_entry_point("investigator")
workflow.add_edge("investigator", "risk_assessor")
workflow.add_edge("risk_assessor", END)

app_graph = workflow.compile()
