from typing import Dict, Any
from langgraph.graph import StateGraph, END
from ..mcp_schema import MCPEnvelope
from ..context_curator import ContextCurator

# State Definition
class PgState(Dict[str, Any]):
    action: str
    mcp_context: MCPEnvelope
    health_report: Dict[str, Any]
    status: str

curator = ContextCurator()

# Nodes
def monitor_programs_node(state: PgState):
    print(">>> [PgMA] Aggregating Program Context...")
    ctx = curator.build_pgma_context()
    return {"mcp_context": ctx}

def analyze_dependencies_node(state: PgState):
    ctx = state['mcp_context']
    critical_blockers = []
    
    # Simulate logic finding cycles or bottlenecks
    if ctx.dependency.cross_team_dependencies:
        for dep in ctx.dependency.cross_team_dependencies:
            if "blocked by" in dep:
                critical_blockers.append(dep)
                
    print(f">>> [PgMA] Found {len(critical_blockers)} critical cross-team blockers.")
    
    return {
        "health_report": {
            "overall_status": "AMBER",
            "critical_path_blockers": critical_blockers,
            "risk_heatmap": ctx.risk.risk_heatmap,
            "recommendation": "Initiate Swarm Session for Legacy API Team"
        }
    }

def generate_report_node(state: PgState):
    # Just a pass-through for now, could act as formatting step
    return {"status": "REPORT_READY"}

# Graph Construction
workflow = StateGraph(PgState)

workflow.add_node("monitor_programs", monitor_programs_node)
workflow.add_node("analyze_dependencies", analyze_dependencies_node)
workflow.add_node("generate_report", generate_report_node)

workflow.set_entry_point("monitor_programs")
workflow.add_edge("monitor_programs", "analyze_dependencies")
workflow.add_edge("analyze_dependencies", "generate_report")
workflow.add_edge("generate_report", END)

from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
pg_graph = workflow.compile(checkpointer=checkpointer)
