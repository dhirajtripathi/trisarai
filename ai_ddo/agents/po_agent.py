from langchain_core.messages import HumanMessage, SystemMessage
from ..llm_factory import LLMFactory
import json

from ..mcp_schema import MCPEnvelope
from ..context_curator import ContextCurator
from typing import TypedDict, List
from langgraph.graph import StateGraph, END

# --- State ---
class POState(TypedDict):
    input_feature: str
    mcp_context: MCPEnvelope
    generated_stories: List[dict]
    human_feedback: str
    final_output: dict

# --- Nodes ---
def retrieve_context_node(state: POState):
    """
    Curates the Context Envelope based on the input feature.
    """
    curator = ContextCurator()
    envelope = curator.build_po_context(objective=f"Refine feature: {state['input_feature']}")
    return {"mcp_context": envelope}

def generate_stories_node(state: POState):
    """
    Uses LLM (Azure/AWS/Gemini) to generate stories from Context.
    """
    ctx = state['mcp_context']
    feature = state['input_feature']
    
    llm = LLMFactory.get_llm()
    print(f"🤖 [PO Agent] Using Provider: {llm._llm_type}")

    if llm._llm_type == "mock":
        # Return Deterministic Mock Data for Demo Stability
        print(f"   [Mock Mode] Returning canned stories for '{feature}'...")
        mock_stories = [
            {
                "title": f"Setup {feature} Backend",
                "description": "Create API endpoints...",
                "ac": "Given API is called, Then return 200.",
                "sp": 5,
                "wsjf": 8.5
            },
            {
                "title": f"Build {feature} UI",
                "description": "Create React components...",
                "ac": "Given user clicks button, Then show notification.",
                "sp": 3,
                "wsjf": 5.0
            }
        ]
        return {"generated_stories": mock_stories}
    
    else:
        # Real LLM Call
        system_prompt = f"""You are a Product Owner Agent.
        Context: {ctx.task.objective}.
        Role: {ctx.role.name}.
        Return a JSON list of User Stories with 'title', 'description', 'ac', 'sp', 'wsjf'."""
        
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Generate stories for feature: {feature}")
        ])
        
        # Simplified parsing for PoC (in prod, use OutputParsers)
        try:
            content = response.content.replace("```json", "").replace("```", "")
            generated_stories = json.loads(content)
            return {"generated_stories": generated_stories}
        except Exception as e:
            print(f"!!! Error parsing LLM response: {e}")
            return {"generated_stories": []}

def human_approval_node(state: POState):
    # This node runs AFTER interrupt.
    # state['human_feedback'] should be set by the API resume.
    print(f"👤 Human Feedback Received: {state.get('human_feedback')}")
    return {}

def finalize_backlog_node(state: POState):
    stories = state['generated_stories']
    if state.get('human_feedback') == "APPROVE":
        from ..config_store import ConfigStore
        import requests
        from requests.auth import HTTPBasicAuth
        
        store = ConfigStore()
        config = store.get_config()
        jira_conf = config.get("jira_config", {})
        
        # Normalize URL
        url_base = jira_conf.get("url", "").rstrip("/")
        email = jira_conf.get("email")
        token = jira_conf.get("api_token")
        # Support both 'project_key' and 'space_key' legacy
        project_key = jira_conf.get("project_key") or jira_conf.get("space_key")
        
        created_keys = []
        
        if url_base and email and token and project_key:
            print(f"🚀 [PO Agent] Pushing {len(stories)} stories to Jira Project '{project_key}' at {url_base}...")
            
            auth = HTTPBasicAuth(email, token)
            headers = {"Accept": "application/json", "Content-Type": "application/json"}
            api_endpoint = f"{url_base}/rest/api/3/issue"
            
            for story in stories:
                # Append AC and WSJF to description for visibility
                full_desc = (
                    f"{story.get('description')}\n\n"
                    f"*Acceptance Criteria:*\n{story.get('ac')}\n\n"
                    f"-----\n*AI-DDO Metrics:*\n* WSJF Score: {story.get('wsjf')}\n* Est. SP: {story.get('sp')}"
                )
                
                payload = {
                    "fields": {
                        "project": {"key": project_key},
                        "summary": story.get("title"),
                        "description": {
                            "type": "doc",
                            "version": 1,
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {"type": "text", "text": full_desc}
                                    ]
                                }
                            ]
                        },
                        "issuetype": {"name": "Story"}
                    }
                }
                
                # Check if description needs simpler format (string vs ADF)
                # Some Jira Cloud instances enforce ADF (Atlassian Document Format).
                # Fallback to simple string description if ADF fails or for older APIs?
                # Actually, strictly speaking v3 API requires ADF. v2 uses raw strings.
                # Let's try v2 for compatibility and simplicity if user didn't specify.
                # Actually, let's use v2 API to avoid complex ADF construction for this PoC.
                
                # Try with 'Story' first, then 'Task'
                issue_types_to_try = ["Story", "Task", "Bug"]
                
                # Define endpoint here to ensure scope availability
                api_endpoint_v2 = f"{url_base}/rest/api/2/issue"
                
                success = False
                for itype in issue_types_to_try:
                    if success: break
                    
                    payload_v2 = {
                        "fields": {
                            "project": {"key": project_key},
                            "summary": story.get("title"),
                            "description": full_desc,
                            "issuetype": {"name": itype}
                        }
                    }

                    try:
                        print(f"   [..] Trying Issue Type: {itype}")
                        resp = requests.post(api_endpoint_v2, json=payload_v2, headers=headers, auth=auth)
                        if resp.status_code in [201, 200]:
                            key = resp.json().get("key")
                            created_keys.append(key)
                            print(f"   ✅ Created {key} ({itype})")
                            success = True
                        else:
                            print(f"   ⚠️ Failed as {itype}: {resp.status_code} - {resp.text}")
                    except Exception as e:
                        print(f"   !!! Network Error: {e}")
                        break # Don't retry on network error
                        
            print(f"🏁 Sync Complete. Created {len(created_keys)} tickets.")
            return {"final_output": {"status": "SYNCED_TO_JIRA", "count": len(created_keys), "keys": created_keys}}
            
        else:
            print("⚠️ Jira credentials missing or incomplete. Skipping real sync.")
            print("✅ Stories pushed to [Mock] Backlog.")
            return {"final_output": {"status": "COMMITTED_LOCALLY", "count": len(stories)}}
            
    else:
        print("❌ Stories rejected.")
        return {"final_output": {"status": "REJECTED", "count": 0}}

# --- Graph ---
def build_po_graph():
    workflow = StateGraph(POState)
    
    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("generate_stories", generate_stories_node)
    workflow.add_node("human_approval", human_approval_node)
    workflow.add_node("finalize_backlog", finalize_backlog_node)
    
    workflow.set_entry_point("retrieve_context")
    
    workflow.add_edge("retrieve_context", "generate_stories")
    workflow.add_edge("generate_stories", "human_approval")
    workflow.add_edge("human_approval", "finalize_backlog")
    workflow.add_edge("finalize_backlog", END)
    
    from langgraph.checkpoint.memory import MemorySaver
    checkpointer = MemorySaver()
    return workflow.compile(interrupt_before=["human_approval"], checkpointer=checkpointer)

po_graph = build_po_graph()
