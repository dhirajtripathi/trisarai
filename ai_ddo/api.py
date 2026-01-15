from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import uvicorn
from contextlib import asynccontextmanager

from .agents.po_agent import po_graph
from .agents.sm_agent import sm_graph
from .agents.pm_agent import pm_graph
from .agents.proj_agent import proj_graph
from .agents.pg_agent import pg_graph
from .agents.orch_agent import orch_graph
from .config_store import ConfigStore

# --- Persistence (In-Memory for PoC) ---
# In production, use SqliteSaver or PostgresSaver
threads = {} 

app = FastAPI(title="AI-DDO API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Graphs (Imported above) ---
# po_graph, sm_graph, etc are already instantiated in their modules

# --- Models ---
class FeatureRequest(BaseModel):
    feature: str

class ApprovalRequest(BaseModel):
    thread_id: str
    decision: str # APPROVE / REJECT

class SMRequest(BaseModel):
    action: str # "analyze"

# --- Endpoints: Product Owner ---

@app.post("/po/draft")
async def draft_stories(req: FeatureRequest):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # Start Graph
    initial_state = {"input_feature": req.feature}
    
    # We use stream or invoke. Since we have interrupt, we expect it to stop.
    # We run until the interrupt.
    events = []
    async for event in po_graph.astream(initial_state, config):
        events.append(event)
        
    # Get current state to show to UI
    snapshot = po_graph.get_state(config)
    
    # Save thread config for later resume
    threads[thread_id] = "po"
    
    return {
        "thread_id": thread_id,
        "status": "WAITING_FOR_REVIEW",
        "generated_context": snapshot.values.get("mcp_context"),
        "stories": snapshot.values.get("generated_stories", [])
    }

@app.post("/po/approve")
async def approve_stories(req: ApprovalRequest):
    thread_id = req.thread_id
    config = {"configurable": {"thread_id": thread_id}}
    
    # Update State with Decision
    po_graph.update_state(config, {"human_feedback": req.decision})
    
    # Resume
    final_output = None
    async for event in po_graph.astream(None, config):
        for v in event.values():
            if "final_output" in v:
                final_output = v["final_output"]
                
    return {"status": "COMPLETED", "result": final_output}

# --- Endpoints: Scrum Master ---

@app.post("/sm/analyze")
async def analyze_sprint(req: SMRequest):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {"anomalies": []} # inputs
    
    snapshot = None
    async for event in sm_graph.astream(initial_state, config):
        pass
        
    snapshot = sm_graph.get_state(config)
    
    # Check if we stopped at interrupt
    if snapshot.next:
        return {
            "thread_id": thread_id,
            "status": "ALERT_TRIGGERED",
            "anomalies": snapshot.values.get("anomalies", [])
        }
    else:
        return {
            "thread_id": thread_id,
            "status": "HEALTHY",
            "anomalies": []
        }

@app.post("/sm/acknowledge")
async def ack_alert(req: ApprovalRequest):
    thread_id = req.thread_id
    config = {"configurable": {"thread_id": thread_id}}
    
    sm_graph.update_state(config, {"human_ack": req.decision})
    
    async for event in sm_graph.astream(None, config):
        pass
        
    return {"status": "ACKNOWLEDGED"}

# --- Endpoints: Product Manager (PMA) ---

class PMRequest(BaseModel):
    goal: str

@app.post("/pma/roadmap")
async def generate_roadmap(req: PMRequest):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {"input_goal": req.goal}
    
    async for event in pm_graph.astream(initial_state, config):
        pass
        
    snapshot = pm_graph.get_state(config)
    
    return {
        "thread_id": thread_id,
        "status": snapshot.values.get("status", "UNKNOWN"),
        "roadmap": snapshot.values.get("roadmap", [])
    }

@app.post("/pma/approve")
async def approve_roadmap(req: ApprovalRequest):
    thread_id = req.thread_id
    config = {"configurable": {"thread_id": thread_id}}
    
    # Resume after interrupt
    pm_graph.update_state(config, {"human_feedback": req.decision})
    
    async for event in pm_graph.astream(None, config):
        pass
        
    return {"status": "PUBLISHED"}

# --- Endpoints: Project Manager (ProjMA) ---

class ProjRequest(BaseModel):
    action: str

@app.post("/projma/forecast")
async def forecast_delivery(req: ProjRequest):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {} 
    
    async for event in proj_graph.astream(initial_state, config):
        pass
    
    snapshot = proj_graph.get_state(config)
    return {
        "thread_id": thread_id,
        "forecast": snapshot.values.get("forecast"),
        "risks": snapshot.values.get("risks", [])
    }

# --- Endpoints: Program Manager (PgMA) ---

@app.post("/pgma/health")
async def check_program_health(req: ProjRequest):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    async for event in pg_graph.astream({}, config):
        pass
        
    snapshot = pg_graph.get_state(config)
    return {"report": snapshot.values.get("health_report")}

# --- Endpoints: Orchestrator (Orch) ---

@app.post("/orch/govern")
async def enforce_governance(req: ProjRequest):
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    async for event in orch_graph.astream({}, config):
        pass
        
    snapshot = orch_graph.get_state(config)
    return {
        "status": snapshot.values.get("status"),
        "decision": snapshot.values.get("policy_decision")
    }

# --- Endpoints: Configuration ---

@app.get("/config")
async def get_config():
    store = ConfigStore()
    return store.get_config()

class ConfigUpdateRequest(BaseModel):
    config: dict

@app.post("/config")
async def update_config(req: ConfigUpdateRequest):
    store = ConfigStore()
    store.update_config(req.config)
    return {"status": "UPDATED", "config": store.get_config()}

@app.post("/config/test-llm")
async def test_llm_connection(req: ConfigUpdateRequest):
    """
    Tests the LLM connection using the provided configuration (without saving).
    """
    try:
        from .llm_factory import LLMFactory
        from langchain_core.messages import HumanMessage
        
        # Instantiate LLM with config override
        llm = LLMFactory.get_llm(config_override=req.config)
        
        # Try a simple invocation
        response = llm.invoke([HumanMessage(content="Hello, reply with 'OK'.")])
        
        return {"status": "SUCCESS", "message": f"Connected! Response: {response.content}"}
    except Exception as e:
        print(f"!!! LLM Test Failed: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/config/test-jira")
async def test_jira_connection(req: ConfigUpdateRequest):
    """
    Tests the Jira connection using the provided configuration.
    """
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        jira_config = req.config.get("jira_config", {})
        url = jira_config.get("url", "").rstrip("/")
        email = jira_config.get("email")
        token = jira_config.get("api_token")
        
        if not url or not email or not token:
             return {"status": "error", "message": "Missing Jira URL, Email, or API Token."}

        # Test "Myself" endpoint
        api_url = f"{url}/rest/api/3/myself"
        
        response = requests.get(
            api_url,
            auth=HTTPBasicAuth(email, token),
            headers={"Accept": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {"status": "SUCCESS", "message": f"Connected as {data.get('displayName')} ({data.get('emailAddress')})"}
        else:
            return {"status": "error", "message": f"Jira Error {response.status_code}: {response.text}"}

    except Exception as e:
        print(f"!!! Jira Test Failed: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)
