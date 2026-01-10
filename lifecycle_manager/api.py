from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
from agent import agent_graph, AgentState
from data_models import CustomerProfile, LifeEvent
from config import Config

app = FastAPI(title="Policy Lifecycle Manager API")

# In-memory customer (for demo purposes)
current_customer = CustomerProfile(
    id="CUST-101",
    name="Alex Doe",
    age=29,
    existing_policies=["Renters"],
    annual_premium=250.00,
    risk_score=20
)

class EventRequest(BaseModel):
    event_type: str
    description: str
    # Provider Selection
    provider: Optional[str] = "Azure OpenAI"
    # Credentials
    azure_key: Optional[str] = None
    azure_endpoint: Optional[str] = None
    azure_deployment: Optional[str] = None
    azure_api_version: Optional[str] = None
    
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None
    aws_region: Optional[str] = None
    aws_model_id: Optional[str] = None
    
    google_key: Optional[str] = None
    google_model: Optional[str] = None

@app.get("/customer")
async def get_customer():
    return current_customer.model_dump()

@app.post("/simulate-event")
async def simulate_event(request: EventRequest):
    event = LifeEvent(
        event_type=request.event_type,
        description=request.description,
        timestamp="NOW"
    )

    # Pack credentials
    creds = {
        "azure_key": request.azure_key,
        "azure_endpoint": request.azure_endpoint,
        "azure_deployment": request.azure_deployment,
        "azure_api_version": request.azure_api_version,
        "aws_access_key": request.aws_access_key,
        "aws_secret_key": request.aws_secret_key,
        "aws_region": request.aws_region,
        "aws_model_id": request.aws_model_id,
        "google_key": request.google_key,
        "google_model": request.google_model
    }

    initial_state = {
        "customer": current_customer,
        "event": event,
        "proposal": None,
        "draft_message": "",
        "provider": request.provider,
        "credentials": creds
    }

    try:
        result = agent_graph.invoke(initial_state)
        return {
            "proposal": result["proposal"].model_dump(),
            "draft_message": result["draft_message"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
