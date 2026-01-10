from typing import TypedDict, List
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from langchain_aws import ChatBedrock
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from config import Config
from rag_knowledge import get_retriever
import os

# Define State
class AgentState(TypedDict):
    draft_text: str
    relevant_regulations: List[str]
    compliance_status: str  # "COMPLIANT" or "VIOLATION"
    feedback: str
    final_output: str
    llm_provider: str # "Azure OpenAI", "AWS Bedrock", "Google Gemini"
    # Credentials (Optional - to be passed if not in env)
    api_key: str
    endpoint: str
    aws_access_key: str
    aws_secret_key: str
    aws_region: str
    google_key: str
    # Extended Params
    azure_deployment: str
    azure_api_version: str
    aws_model_id: str
    google_model: str

def get_llm(provider, state: AgentState = None):
    # Helper to get value from state OR env
    def get_val(state_key, env_key, default=None):
        if state and state.get(state_key):
             return state[state_key]
        return os.environ.get(env_key) or default

    if provider == "Azure OpenAI":
        return AzureChatOpenAI(
            azure_endpoint=get_val("endpoint", "AZURE_OPENAI_ENDPOINT", Config.AZURE_OPENAI_ENDPOINT),
            api_key=get_val("api_key", "AZURE_OPENAI_API_KEY", Config.AZURE_OPENAI_API_KEY),
            api_version=get_val("azure_api_version", "AZURE_OPENAI_API_VERSION", Config.AZURE_OPENAI_API_VERSION),
            deployment_name=get_val("azure_deployment", "AZURE_OPENAI_DEPLOYMENT_NAME", Config.AZURE_OPENAI_DEPLOYMENT_NAME),
            temperature=0
        )
    elif provider == "AWS Bedrock":
        return ChatBedrock(
            model_id=get_val("aws_model_id", "BEDROCK_MODEL_ID", Config.BEDROCK_MODEL_ID),
            region_name=get_val("aws_region", "AWS_DEFAULT_REGION", Config.AWS_DEFAULT_REGION),
            aws_access_key_id=get_val("aws_access_key", "AWS_ACCESS_KEY_ID", Config.AWS_ACCESS_KEY_ID),
            aws_secret_access_key=get_val("aws_secret_key", "AWS_SECRET_ACCESS_KEY", Config.AWS_SECRET_ACCESS_KEY),
             temperature=0
        )
    elif provider == "Google Gemini":
        return ChatGoogleGenerativeAI(
            model=get_val("google_model", "GOOGLE_MODEL_NAME", Config.GOOGLE_MODEL_NAME),
            google_api_key=get_val("google_key", "GOOGLE_API_KEY", Config.GOOGLE_API_KEY),
            temperature=0
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")

# Nodes
def retrieve_regulations(state: AgentState):
    print("---RETRIEVING REGULATIONS---")
    draft = state["draft_text"]
    retriever = get_retriever()
    docs = retriever.invoke(draft)
    regulations = [f"{doc.metadata['source']}: {doc.page_content}" for doc in docs]
    return {"relevant_regulations": regulations}

def check_compliance(state: AgentState):
    print(f"---CHECKING COMPLIANCE with {state['llm_provider']}---")
    llm = get_llm(state["llm_provider"], state)
    draft = state["draft_text"]
    regs = "\n".join(state["relevant_regulations"])
    
    system_prompt = (
        "You are a strict Compliance Officer AI. Your job is to check if a draft response violates any of the provided regulations.\n"
        "If it violates, respond with 'VIOLATION' followed by a brief explanation.\n"
        "If it is compliant, respond with 'COMPLIANT'.\n"
        "Regulations:\n" + regs
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Draft Response: {draft}")
    ]
    
    response = llm.invoke(messages)
    content = response.content.strip()
    
    if "VIOLATION" in content:
        status = "VIOLATION"
        feedback = content.replace("VIOLATION", "").strip()
    else:
        status = "COMPLIANT"
        feedback = "No violations found."
        
    return {"compliance_status": status, "feedback": feedback}

def guardrail_rewrite(state: AgentState):
    print(f"---GUARDRAIL REWRITE with {state['llm_provider']}---")
    llm = get_llm(state["llm_provider"], state)
    draft = state["draft_text"]
    regs = "\n".join(state["relevant_regulations"])
    feedback = state["feedback"]
    
    system_prompt = (
        "You are a Compliance Guardrail Bot. The user's draft violates regulations.\n"
        "Rewrite the draft to be fully compliant with the regulations provided.\n"
        "Maintain the original intent as much as possible, but strictly adhere to the rules.\n"
        "Regulations:\n" + regs + "\n\n"
        "violation Details: " + feedback
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Original Draft: {draft}")
    ]
    
    response = llm.invoke(messages)
    return {"final_output": response.content}

def pass_through(state: AgentState):
    # If compliant, the final output is just the draft
    return {"final_output": state["draft_text"]}

# Conditional Logic
def should_rewrite(state: AgentState):
    if state["compliance_status"] == "VIOLATION":
        return "rewrite"
    return "pass"

# Build Graph
builder = StateGraph(AgentState)

builder.add_node("retrieve", retrieve_regulations)
builder.add_node("check", check_compliance)
builder.add_node("rewrite", guardrail_rewrite)
builder.add_node("pass", pass_through)

builder.set_entry_point("retrieve")
builder.add_edge("retrieve", "check")

builder.add_conditional_edges(
    "check",
    should_rewrite,
    {
        "rewrite": "rewrite",
        "pass": "pass"
    }
)

builder.add_edge("rewrite", END)
builder.add_edge("pass", END)

graph = builder.compile()
