from typing import TypedDict, Annotated, List, Any, Optional, Dict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import os
from langchain_core.messages import HumanMessage
from langchain_openai import AzureChatOpenAI
from langchain_aws import ChatBedrock
from langchain_google_genai import ChatGoogleGenerativeAI
from config import Config
from utils.iot_tools import fetch_ehr, fetch_wearable_data
from utils.risk_engine import analyze_risk

# 1. State Definition
class UnderwriterState(TypedDict):
    user_id: str
    
    # Provider Info
    provider: str
    credentials: Dict[str, Any]
    
    medical_history: List[dict]
    wearable_stats: dict
    risk_analysis: dict
    human_decision: str # "Approve", "Reject", "Override"
    final_policy: dict

# 2. LLM Helper
def get_llm(provider: str, creds: Dict[str, Any]):
    if provider == "Azure OpenAI":
        return AzureChatOpenAI(
            azure_endpoint=creds.get("azure_endpoint") or Config.AZURE_OPENAI_ENDPOINT,
            api_key=creds.get("azure_key") or Config.AZURE_OPENAI_API_KEY,
            api_version=creds.get("azure_api_version") or Config.AZURE_OPENAI_API_VERSION,
            deployment_name=creds.get("azure_deployment") or Config.AZURE_OPENAI_DEPLOYMENT_NAME,
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
def data_ingestion_node(state: UnderwriterState):
    print("---DATA INGESTION---")
    user_id = state['user_id']
    ehr = fetch_ehr.invoke(user_id)
    wearables = fetch_wearable_data.invoke(user_id)
    
    return {
        "medical_history": ehr,
        "wearable_stats": wearables
    }

def risk_analysis_node(state: UnderwriterState):
    print("---RISK ANALYSIS---")
    # In a real scenario, LLM would be used for unstructured analysis.
    # Here we are mostly using the rule-based risk_engine, but we can augment it with LLM summary.
    
    analysis = analyze_risk(state['medical_history'], state['wearable_stats'])
    
    # Optional: Use LLM to generate the reasoning text dynamically
    provider = state.get("provider", "Azure OpenAI")
    creds = state.get("credentials", {})
    
    try:
        llm = get_llm(provider, creds)
        prompt = f"""
        Analyze the following risk factors and generate a professional underwriting reasoning summary.
        Risk Factors: {analysis['relevant_conditions']}
        Wearable Bonus: {'Yes' if state['wearable_stats']['avg_daily_steps'] > 5000 else 'No'}
        """
        # For simplicity in this PoC, we are skipping the actual LLM call to save time/tokens if keys aren't set,
        # but the infrastructure is here.
        # analysis['reasoning'] = llm.invoke([HumanMessage(content=prompt)]).content
        pass
    except Exception as e:
        print(f"LLM Reasoning Failed: {e}")

    return {"risk_analysis": analysis}

def human_approval_node(state: UnderwriterState):
    print("---HUMAN APPROVAL (Resume)---")
    # This node runs AFTER the interrupt. 
    # The 'human_decision' is injected via update_state from the UI.
    return {} 

def finalize_policy_node(state: UnderwriterState):
    print("---FINALIZE POLICY---")
    decision = state.get('human_decision')
    analysis = state['risk_analysis']
    
    if decision == "Approve":
        policy = {
            "status": "Active",
            "premium": analysis['suggested_premium'],
            "conditions": analysis['nudges']
        }
    else:
        policy = {"status": "Rejected", "reason": "Underwriter Decision"}
        
    return {"final_policy": policy}

# 4. Graph Construction
def build_graph():
    # Setup checkpointer
    conn = sqlite3.connect(Config.DB_PATH, check_same_thread=False)
    memory = SqliteSaver(conn)
    
    workflow = StateGraph(UnderwriterState)
    
    workflow.add_node("data_ingestion", data_ingestion_node)
    workflow.add_node("risk_analysis", risk_analysis_node)
    workflow.add_node("human_approval", human_approval_node)
    workflow.add_node("finalize_policy", finalize_policy_node)
    
    workflow.set_entry_point("data_ingestion")
    
    workflow.add_edge("data_ingestion", "risk_analysis")
    workflow.add_edge("risk_analysis", "human_approval")
    workflow.add_edge("human_approval", "finalize_policy")
    workflow.add_edge("finalize_policy", END)
    
    # COMPILE WITH INTERRUPT
    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["human_approval"]
    )

app_graph = build_graph()
