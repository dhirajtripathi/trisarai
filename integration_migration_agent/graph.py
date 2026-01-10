from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import AzureChatOpenAI
from langchain_aws import ChatBedrock
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

from .utils.prompt_loader import load_prompt
from .utils.rag_engine import RAGEngine
from .config import DB_PATH

# 1. State Definition
class MigrationState(TypedDict):
    # Inputs
    source_files: Dict[str, str] # filename -> content
    source_system: str
    target_system: str
    provider: str
    credentials: Dict[str, str]
    
    # Generated Artifacts
    srs_content: Optional[str]
    arch_diagram: Optional[str]
    generated_code: Optional[str]
    test_cases: Optional[str]
    implementation_steps: Optional[str]
    
    # Internal
    rag_engine: Optional[object] # Not serializable usually, re-init?
    # We won't store the engine object in state, just use it transiently or rebuild

# 2. LLM Helper
def get_llm(state: MigrationState):
    provider = state.get("provider", "Azure OpenAI")
    creds = state.get("credentials", {})
    
    if provider == "Azure OpenAI":
        return AzureChatOpenAI(
            api_key=creds.get("azure_key"),
            azure_endpoint=creds.get("azure_endpoint"),
            deployment_name=creds.get("azure_deployment", "gpt-4"),
            api_version=creds.get("azure_api_version", "2023-05-15"),
            temperature=0
        )
    elif provider == "AWS Bedrock":
        return ChatBedrock(
            credentials_profile_name=None,
            aws_access_key_id=creds.get("aws_access_key"),
            aws_secret_access_key=creds.get("aws_secret_key"),
            region_name=creds.get("aws_region", "us-east-1"),
            model_id=creds.get("aws_model_id", "anthropic.claude-v2")
        )
    elif provider == "Google Gemini":
        return ChatGoogleGenerativeAI(
            google_api_key=creds.get("google_key"),
            model=creds.get("google_model", "gemini-pro")
        )
    return None

# 3. Nodes

def reverse_engineer_node(state: MigrationState):
    """Generates SRS from Source Files"""
    llm = get_llm(state)
    files = state["source_files"]
    source_sys = state["source_system"]
    
    # Spin up RAG
    rag = RAGEngine(provider=state.get("provider"), creds=state.get("credentials"))
    rag.ingest_files(files, platform=source_sys)
    
    # Simple dump of all code
    all_code = "\n".join([f"--- {k} ---\n{v}" for k,v in files.items()])
    
    # Query RAG for best practices/migration rules related to this code
    # We use a generic query or specific keywords from the code
    context = rag.retrieve_context("migration best practices patterns errors", k=3)
    
    prompt_template = load_prompt("srs_generation", source_sys, "source")
    # Fill prompt
    prompt = prompt_template.format(system_name=source_sys, context_str=context, source_code=all_code)
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"srs_content": response.content}

def architect_node(state: MigrationState):
    """Generates Architecture from SRS"""
    llm = get_llm(state)
    srs = state["srs_content"]
    target_sys = state["target_system"]
    
    prompt_template = load_prompt("architecture", target_sys, "target")
    prompt = prompt_template.format(system_name=target_sys, srs_content=srs)
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"arch_diagram": response.content}

def coder_node(state: MigrationState):
    """Generates Code from SRS & Arch"""
    llm = get_llm(state)
    srs = state["srs_content"]
    arch = state["arch_diagram"]
    target_sys = state["target_system"]
    
    prompt_template = load_prompt("code_generation", target_sys, "target")
    prompt = prompt_template.format(system_name=target_sys, srs_content=srs, arch_content=arch)
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"generated_code": response.content}

def qa_node(state: MigrationState):
    """Generates Unit Tests & Steps"""
    llm = get_llm(state)
    code = state["generated_code"]
    
    prompt = f"""
    Based on the following generated code, please provide:
    1. Implementation Steps (step-by-step guide for developers).
    2. Unit Test Cases (framework appropriate for {state['target_system']}).
    
    CODE:
    {code}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"test_cases": response.content}

# 4. Graph Construction
workflow = StateGraph(MigrationState)

workflow.add_node("reverse_engineer", reverse_engineer_node)
workflow.add_node("architect", architect_node)
workflow.add_node("coder", coder_node)
workflow.add_node("qa", qa_node)

# Flow
workflow.set_entry_point("reverse_engineer")
workflow.add_edge("reverse_engineer", "architect") # Interrupt happens here in app usage logic, using interrupt_before?
# Actually, the requirement says "Once generated SRS then it should have option to display and download it for human in the loop approach."
# So we need to stop AFTER reverse_engineer.

workflow.add_edge("architect", "coder")
workflow.add_edge("coder", "qa")
workflow.add_edge("qa", END)

# Persistence
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
memory = SqliteSaver(conn)

# Compile with interrupt
app = workflow.compile(checkpointer=memory, interrupt_after=["reverse_engineer"])
