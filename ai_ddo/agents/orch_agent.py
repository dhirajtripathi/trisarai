from typing import Dict, Any
from langgraph.graph import StateGraph, END
from ..mcp_schema import MCPEnvelope
from ..context_curator import ContextCurator

# State Definition
class OrchState(Dict[str, Any]):
    action: str
    mcp_context: MCPEnvelope
    policy_decision: Dict[str, Any]
    status: str

curator = ContextCurator()

# Nodes
def check_policy_node(state: OrchState):
    print(">>> [ORCH] Verifying Portfolio Governance...")
    ctx = curator.build_orch_context()
    return {"mcp_context": ctx}

def enforce_gates_node(state: OrchState):
    ctx = state['mcp_context']
    violations = []
    
    # LLM-based Policy Check
    from ..llm_factory import LLMFactory
    from langchain_core.messages import SystemMessage, HumanMessage
    import json

    llm = LLMFactory.get_llm()
    
    system_prompt = """You are a Portfolio Orchestrator (Governance Agent).
    Audit the provided context against active policies.
    
    Return a valid JSON object with:
    - "decision": "PROCEED" or "PAUSE_FUNDING"
    - "violations": List of strings (empty if none)
    - "required_action": String (e.g. "None", "EVP Approval")
    """
    
    user_prompt = f"""
    Context:
    - Policies: {ctx.portfolio.policies}
    - Budget Burn: {ctx.financial.budget_burn} (Threshold: >1.05 is a violation)
    - Risk Map: {ctx.risk.risk_heatmap}
    
    Identify any violations. If Budget Burn > 1.05, you MUST flag it.
    """
    
    try:
        response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
        content = response.content.strip()
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        policy_decision = json.loads(content)
        
        status = "GATE_LOCKED" if policy_decision["decision"] == "PAUSE_FUNDING" else "APPROVED"
        
    except Exception as e:
        print(f"!!! [ORCH] LLM Error: {e}")
        status = "GATE_LOCKED" # Fail safe
        policy_decision = {"decision": "ERROR", "violations": [str(e)], "required_action": "Retry"}

    return {
        "policy_decision": policy_decision,
        "status": status
    }

# Graph Construction
workflow = StateGraph(OrchState)

workflow.add_node("check_policy", check_policy_node)
workflow.add_node("enforce_gates", enforce_gates_node)

workflow.set_entry_point("check_policy")
workflow.add_edge("check_policy", "enforce_gates")
workflow.add_edge("enforce_gates", END) 

from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
orch_graph = workflow.compile(checkpointer=checkpointer)
