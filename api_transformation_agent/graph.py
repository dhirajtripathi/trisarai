from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from api_transformation_agent.uam_schema import UAMEnvelope
from api_transformation_agent.llm_utils import get_llm

# Parsers & Generators
from api_transformation_agent.parsers.apigee_parser import ApigeeParser
from api_transformation_agent.parsers.kong_parser import KongParser
from api_transformation_agent.parsers.azure_parser import AzureParser
from api_transformation_agent.parsers.generic_parser import GenericLLMParser

from api_transformation_agent.generators.kong_generator import KongGenerator
from api_transformation_agent.generators.azure_generator import AzureGenerator
from api_transformation_agent.generators.apigee_generator import ApigeeGenerator
from api_transformation_agent.generators.generic_generator import GenericLLMGenerator

class TransformationState(TypedDict):
    # Inputs
    source_type: str
    target_type: str
    source_path: str
    config: Dict[str, Any] # LLM Config
    
    # Artifacts
    uam: Optional[UAMEnvelope]
    critique: Optional[str]
    generated_config: Optional[str]

    # Meta
    error: Optional[str]

def parsing_node(state: TransformationState):
    """Selects parser and generates UAM"""
    source_type = state["source_type"]
    source_path = state["source_path"]
    
    try:
        if source_type == "apigee":
            parser = ApigeeParser()
        elif source_type == "kong":
            parser = KongParser()
        elif source_type == "azure":
            parser = AzureParser()
        else:
            parser = GenericLLMParser(source_type)
        
        uam = parser.parse(source_path)
        return {"uam": uam}
    except Exception as e:
        return {"error": str(e)}

def critique_node(state: TransformationState):
    """
    Agentic Step: self-reflection.
    Checks if the UAM looks valid or has logical gaps.
    """
    if state.get("error"):
        return {}

    uam = state["uam"]
    llm = get_llm(state["config"])
    
    # We serialize UAM to JSON for the LLM to review
    uam_json = uam.model_dump_json(indent=2)
    
    prompt = f"""
    You are an API Architect Critic. Review the following Unified API Model (UAM).
    Check for:
    1. Missing Service definitions.
    2. Empty Route paths.
    3. Logical inconsistencies.
    
    If it looks good, just say "APPROVED".
    If there are issues, list them briefly.
    
    UAM:
    {uam_json}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"critique": response.content}

def generating_node(state: TransformationState):
    """Generates Target Config"""
    if state.get("error"):
        return {}
        
    target_type = state["target_type"]
    uam = state["uam"]
    
    try:
        if target_type == "kong":
            generator = KongGenerator()
        elif target_type == "azure":
            generator = AzureGenerator()
        elif target_type == "apigee":
            generator = ApigeeGenerator()
        else:
            generator = GenericLLMGenerator(target_type)
            
        output = generator.generate(uam)
        return {"generated_config": output}
    except Exception as e:
        return {"error": str(e)}

# --- Graph Contruction ---
workflow = StateGraph(TransformationState)

workflow.add_node("parsing", parsing_node)
workflow.add_node("critiquing", critique_node) # Renamed from critique
workflow.add_node("generating", generating_node)

workflow.set_entry_point("parsing")
workflow.add_edge("parsing", "critiquing")
workflow.add_edge("critiquing", "generating")
workflow.add_edge("generating", END)

# In-Memory checkpointer for now (or SQLite if needed later)
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
