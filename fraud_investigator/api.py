from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from graph import app_graph
from config import Config

app = FastAPI(title="Fraud Investigator API")

# Simulation Data
CLAIMS_DB = [
    {
        "id": "CLM-2026-001",
        "name": "John Doe Fake",
        "date": "2026-05-12",
        "desc": "Kitchen fire caused by toaster malfunction.",
        "photo": "kitchen_fire_001",
        "risk_label": "High Risk"
    },
    {
        "id": "CLM-2026-002",
        "name": "Sarah Smith",
        "date": "2026-06-20",
        "desc": "Rear-ended at stop light.",
        "photo": "bumper_dent_04",
        "risk_label": "Low Risk"
    },
    {
        "id": "CLM-2026-003",
        "name": "Project X Party",
        "date": "2026-07-04",
        "desc": "House destroyed by accidental fire while on vacation.",
        "photo": "house_fire_09",
        "risk_label": "Med Risk"
    }
]

class InvestigationRequest(BaseModel):
    claim_id: str
    claimant_name: str
    claim_date: str
    claim_description: str
    photo_id: str
    
    # Provider Config
    provider: str
    credentials: Dict[str, Any]

@app.get("/claims")
async def get_claims():
    return CLAIMS_DB

@app.post("/investigate")
async def investigate(request: InvestigationRequest):
    input_state = {
        "claim_id": request.claim_id,
        "claimant_name": request.claimant_name,
        "claim_date": request.claim_date,
        "claim_description": request.claim_description,
        "photo_id": request.photo_id,
        "provider": request.provider,
        "credentials": request.credentials
    }
    
    try:
        result = app_graph.invoke(input_state)
        return {
            "evidence_log": result.get("evidence_log", []),
            "fraud_score": result.get("fraud_score", 0),
            "risk_reasoning": result.get("risk_reasoning", ""),
            "requires_human_review": result.get("requires_human_review", False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
