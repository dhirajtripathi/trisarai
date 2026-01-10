from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import os
from graph import app_graph
from config import Config

app = FastAPI(title="Claims Adjuster API")

class ClaimRequest(BaseModel):
    image_status: str # "clear" or "blurry"
    voice_transcript: str
    
    # Provider Config
    provider: str
    credentials: Dict[str, Any]

@app.post("/submit")
async def submit_claim(request: ClaimRequest):
    input_state = {
        "image_status": request.image_status,
        "voice_transcript": request.voice_transcript,
        "provider": request.provider,
        "credentials": request.credentials,
        "intake_result": {},
        "policy_context": "",
        "coverage_verdict": {},
        "estimate_details": {},
        "status": "started",
        "final_message": ""
    }
    
    try:
        result = app_graph.invoke(input_state)
        return {
            "status": result.get("status"),
            "final_message": result.get("final_message"),
            "intake_result": result.get("intake_result"),
            "coverage_verdict": result.get("coverage_verdict"),
            "estimate_details": result.get("estimate_details"),
            "policy_context": result.get("policy_context")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
