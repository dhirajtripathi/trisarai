from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
import os
from graph import app_graph
from config import Config

app = FastAPI(title="Underwriting Agent API", description="HITL API for Underwriting")

class StartCaseRequest(BaseModel):
    user_id: str
    provider: str
    credentials: Dict[str, Any]

class ResumeRequest(BaseModel):
    decision: str # "Approve", "Reject"

@app.post("/cases")
async def start_case(request: StartCaseRequest):
    thread_id = f"case_{request.user_id}"
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "user_id": request.user_id,
        "provider": request.provider,
        "credentials": request.credentials
    }
    
    # Run until interrupt
    try:
        app_graph.invoke(initial_state, config=config)
        return {"thread_id": thread_id, "status": "started"}
    except Exception as e:
        # LangGraph might return normally but paused.
        # If it errors out, return 500.
        # Note: If it hits interrupt, invoke returns the state at interrupt, not raising error.
        return {"thread_id": thread_id, "status": "paused_at_interrupt"}

@app.get("/cases/{thread_id}")
async def get_case_state(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    try:
        state_snapshot = app_graph.get_state(config)
    except Exception:
        raise HTTPException(status_code=404, detail="Case not found")
        
    if not state_snapshot.values:
        return {"status": "empty"}
        
    values = state_snapshot.values
    next_node = state_snapshot.next
    
    is_paused = bool(next_node and "human_approval" in next_node)
    
    return {
        "user_id": values.get("user_id"),
        "risk_analysis": values.get("risk_analysis"),
        "final_policy": values.get("final_policy"),
        "is_paused": is_paused,
        "next_step": next_node
    }

@app.post("/cases/{thread_id}/resume")
async def resume_case(thread_id: str, request: ResumeRequest):
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Update state with decision
        app_graph.update_state(config, {"human_decision": request.decision})
        
        # Resume
        for event in app_graph.stream(None, config=config):
            pass
            
        # Get final state
        final_state = app_graph.get_state(config)
        return {
            "status": "completed", 
            "final_policy": final_state.values.get("final_policy")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
