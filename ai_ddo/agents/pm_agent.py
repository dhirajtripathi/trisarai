from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from ..mcp_schema import MCPEnvelope
from ..context_curator import ContextCurator
import random

# State Definition
class PMState(Dict[str, Any]):
    input_goal: str
    mcp_context: MCPEnvelope
    roadmap: List[Dict[str, Any]]
    status: str

curator = ContextCurator()

# Nodes
def retrieve_strategy_node(state: PMState):
    print(">>> [PMA] Retrieving Strategic Context...")
    ctx = curator.build_pma_context(state['input_goal'])
    return {"mcp_context": ctx}

def generate_roadmap_node(state: PMState):
    ctx = state['mcp_context']
    print(f">>> [PMA] Generating Roadmap for goal: {state['input_goal']}")
    
    from ..llm_factory import LLMFactory
    from langchain_core.messages import SystemMessage, HumanMessage
    import json

    llm = LLMFactory.get_llm()
    
    system_prompt = """You are a Strategic Product Manager Agent. 
    Your goal is to generate a quarterly roadmap based on the User's Business Goal and the provided Strategic Context.
    
    Return a valid JSON array of objects. Each object must have:
    - "quarter": e.g. "Q1", "Q2"
    - "theme": High level theme
    - "initiative": Specific project name
    - "okr_alignment": How it aligns with goals (string)
    - "confidence": Float between 0.0 and 1.0
    
    Do NOT return markdown formatting like ```json. Just return the raw JSON array.
    """
    
    user_prompt = f"""
    Business Goal: {state['input_goal']}
    
    Context: {ctx}
    
    Generate 3-5 high-impact roadmap items.
    """
    
    try:
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        initiatives = json.loads(content)
    except Exception as e:
        print(f"!!! [PMA] LLM Error: {e}")
        # Fallback to mock if LLM fails
        initiatives = [
             {
                "theme": "Error Recovery",
                "initiative": "Manual Roadmap Override",
                "okr_alignment": f"Failed to generate: {str(e)}",
                "quarter": "Q1",
                "confidence": 0.0
            }
        ]

    return {"roadmap": initiatives}

def human_review_node(state: PMState):
    # This node is an interrupt
    return {"status": "WAITING_FOR_APPROVAL"}

def finalize_roadmap_node(state: PMState):
    print(">>> [PMA] Roadmap Published to Strategic Memory.")
    return {"status": "PUBLISHED"}

# Graph Construction
workflow = StateGraph(PMState)

workflow.add_node("retrieve_strategy", retrieve_strategy_node)
workflow.add_node("generate_roadmap", generate_roadmap_node)
workflow.add_node("human_review", human_review_node)
workflow.add_node("finalize_roadmap", finalize_roadmap_node)

workflow.set_entry_point("retrieve_strategy")
workflow.add_edge("retrieve_strategy", "generate_roadmap")
workflow.add_edge("generate_roadmap", "human_review")
workflow.add_edge("human_review", "finalize_roadmap")
workflow.add_edge("finalize_roadmap", END)

from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
pm_graph = workflow.compile(checkpointer=checkpointer)
