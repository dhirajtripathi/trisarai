from typing import TypedDict, Optional
import os
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from langchain_aws import ChatBedrock
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from config import Config
from data_models import CustomerProfile, LifeEvent, EndorsementProposal
from pricing_engine import calculate_pricing
import json

class AgentState(TypedDict):
    customer: CustomerProfile
    event: LifeEvent
    proposal: EndorsementProposal
    draft_message: str
    # Provider & Creds
    provider: str
    credentials: dict

# Helper to get LLM
def get_llm(provider: str, creds: dict):
    if provider == "Azure OpenAI":
        return AzureChatOpenAI(
            azure_endpoint=creds.get("azure_endpoint") or Config.AZURE_OPENAI_ENDPOINT,
            api_key=creds.get("azure_key") or Config.AZURE_OPENAI_API_KEY,
            api_version=creds.get("azure_api_version") or Config.AZURE_OPENAI_API_VERSION,
            deployment_name=creds.get("azure_deployment") or Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            temperature=0.7
        )
    elif provider == "AWS Bedrock":
        return ChatBedrock(
            model_id=creds.get("aws_model_id") or "anthropic.claude-v2",
            region_name=creds.get("aws_region") or "us-east-1",
            aws_access_key_id=creds.get("aws_access_key"),
            aws_secret_access_key=creds.get("aws_secret_key"),
            temperature=0.7
        )
    elif provider == "Google Gemini":
        return ChatGoogleGenerativeAI(
            model=creds.get("google_model") or "gemini-pro",
            google_api_key=creds.get("google_key"),
            temperature=0.7
        )
    else:
        # Default fallback
        return AzureChatOpenAI(
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            deployment_name=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
            temperature=0.7
        )

def analyze_and_price(state: AgentState):
    print("---ANALYZING & PRICING---")
    customer = state["customer"]
    event = state["event"]
    
    # Deterministic pricing logic
    proposal = calculate_pricing(customer, event)
    
    return {"proposal": proposal}

def draft_communication(state: AgentState):
    print("---DRAFTING COMMUNICATION---")
    customer = state["customer"]
    event = state["event"]
    proposal = state["proposal"]
    provider = state.get("provider", "Azure OpenAI")
    creds = state.get("credentials", {})
    
    system_prompt = (
        "You are an empathetic and proactive insurance agent.\n"
        "Your goal is to reach out to a customer who has just experienced a major life event.\n"
        "Explain WHY they need this coverage change based on their new situation.\n"
        "Be transparent about the price change.\n"
        "Tone: Professional, Warm, Consultative."
    )
    
    user_prompt = f"""
    Customer: {customer.name} (Age: {customer.age})
    Life Event: {event.event_type} - {event.description}
    
    Recommendation: {proposal.recommended_action} ({proposal.policy_type})
    Reasoning: {proposal.reasoning}
    Premium Change: ${proposal.premium_change:+.2f}
    New Total: ${proposal.new_total_premium:.2f}
    
    Draft a short email/message to the customer.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    try:
        llm = get_llm(provider, creds)
        response = llm.invoke(messages)
        return {"draft_message": response.content}
    except Exception as e:
        return {"draft_message": f"Error generating draft: {str(e)}"}

# Build Graph
builder = StateGraph(AgentState)

builder.add_node("pricing", analyze_and_price)
builder.add_node("drafter", draft_communication)

builder.set_entry_point("pricing")
builder.add_edge("pricing", "drafter")
builder.add_edge("drafter", END)

agent_graph = builder.compile()
