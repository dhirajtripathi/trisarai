from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from ..mcp_schema import MCPEnvelope
from ..context_curator import ContextCurator

# --- State ---
class SMState(TypedDict):
    mcp_context: MCPEnvelope
    anomalies: List[str]
    human_ack: str

# --- Nodes ---
def monitor_flow_node(state: SMState):
    curator = ContextCurator()
    envelope = curator.build_sm_context()
    return {"mcp_context": envelope}

def detect_anomalies_node(state: SMState):
    ctx = state['mcp_context']
    blockers = ctx.team.blockers
    
    if blockers:
        print(f"🚨 [SMA] Detected {len(blockers)} blockers using MCP Context.")
        return {"anomalies": blockers}
    
    return {"anomalies": []}

def notification_node(state: SMState):
    # Interrupt here if anomalies found
    return {}

def log_action_node(state: SMState):
    print(f"📝 Blockers logged/escalated. Human Ack: {state.get('human_ack')}")
    return {}

# --- Graph ---
def build_sm_graph():
    workflow = StateGraph(SMState)
    
    workflow.add_node("monitor_flow", monitor_flow_node)
    workflow.add_node("detect_anomalies", detect_anomalies_node)
    workflow.add_node("notify_human", notification_node)
    workflow.add_node("log_action", log_action_node)
    
    workflow.set_entry_point("monitor_flow")
    workflow.add_edge("monitor_flow", "detect_anomalies")
    
    # Conditional Edge: Only notify if anomalies exist
    def should_notify(state):
        if state['anomalies']:
            return "notify_human"
        return "log_action" # Skip notification if clean
    
    workflow.add_conditional_edges("detect_anomalies", should_notify)
    
    workflow.add_edge("notify_human", "log_action")
    workflow.add_edge("log_action", END)
    
    from langgraph.checkpoint.memory import MemorySaver
    checkpointer = MemorySaver()
    return workflow.compile(interrupt_before=["notify_human"], checkpointer=checkpointer)

sm_graph = build_sm_graph()
