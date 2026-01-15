from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from ..mcp_schema import MCPEnvelope
from ..context_curator import ContextCurator
import random

# State Definition
class ProjState(Dict[str, Any]):
    action: str
    mcp_context: MCPEnvelope
    forecast: Dict[str, Any]
    risks: List[str]
    status: str

curator = ContextCurator()

# Nodes
def monitor_execution_node(state: ProjState):
    print(">>> [ProjMA] Monitoring Execution Context...")
    ctx = curator.build_projma_context()
    return {"mcp_context": ctx}

def forecast_schedule_node(state: ProjState):
    ctx = state['mcp_context']
    capacity = ctx.resource.team_capacity
    backlog_size = delivery_ctx_backlog_size = len(ctx.delivery.backlog_items) or 10 # Default to 10 if empty for testing
    
    from ..llm_factory import LLMFactory
    from langchain_core.messages import SystemMessage, HumanMessage
    import json
    import datetime

    print(f">>> [ProjMA] Forecasting for backlog size: {backlog_size} items")

    llm = LLMFactory.get_llm()
    
    system_prompt = """You are a Project Manager Agent specialized in Agie Forecasting.
    Analyze the project context and predict delivery dates.
    
    Return a valid JSON object (no markdown) with:
    - "target_date": Date string (e.g. "Sept 30")
    - "predicted_date": Date string
    - "variance_days": Integer (positive = late, negative = early)
    - "status": "ON_TRACK" or "AT_RISK"
    """
    
    user_prompt = f"""
    Context:
    - Team Capacity: {capacity}
    - Backlog Items: {backlog_size}
    - Dependencies: {ctx.dependency.cross_team_dependencies}
    - Constraints: {ctx.resource.constraints}
    
    Current Date: {datetime.date.today().strftime("%b %d")}
    Target Release: Sept 30
    
    Estimate the schedule. Simulate some realism based on constraints.
    """
    
    try:
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        forecast_data = json.loads(content)
    except Exception as e:
        print(f"!!! [ProjMA] LLM Error: {e}")
        forecast_data = {
            "target_date": "Sept 30",
            "predicted_date": "Unknown",
            "variance_days": 0,
            "status": "ERROR"
        }

    return {"forecast": forecast_data}

def detect_risks_node(state: ProjState):
    ctx = state['mcp_context']
    risks = []
    
    # Check dependencies
    if ctx.dependency.cross_team_dependencies:
        risks.append(f"dependency_risk: {ctx.dependency.cross_team_dependencies[0]}")
        
    # Check resource constraints
    if ctx.resource.constraints:
        risks.append(f"resource_risk: {ctx.resource.constraints[0]}")
        
    return {"risks": risks, "status": "ANALYSIS_COMPLETE"}

# Graph Construction
workflow = StateGraph(ProjState)

workflow.add_node("monitor_execution", monitor_execution_node)
workflow.add_node("forecast_schedule", forecast_schedule_node)
workflow.add_node("detect_risks", detect_risks_node)

workflow.set_entry_point("monitor_execution")
workflow.add_edge("monitor_execution", "forecast_schedule")
workflow.add_edge("forecast_schedule", "detect_risks")
workflow.add_edge("detect_risks", END)

from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
proj_graph = workflow.compile(checkpointer=checkpointer)
