from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from graph_workflow import graph
from rag_knowledge import add_regulation

app = FastAPI(title="Compliance Bot API")

class ScanRequest(BaseModel):
    draft_text: str
    provider: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None
    aws_region: Optional[str] = None
    google_key: Optional[str] = None
    # Azure Extras
    azure_deployment: Optional[str] = None
    azure_api_version: Optional[str] = None
    # AWS Extras
    aws_model_id: Optional[str] = None
    # Google Extras
    google_model: Optional[str] = None

class ScanResponse(BaseModel):
    compliance_status: str
    feedback: str
    final_output: str
    relevant_regulations: List[str]

@app.post("/scan", response_model=ScanResponse)
async def scan_compliance(request: ScanRequest):
    try:
        initial_state = {
            "draft_text": request.draft_text,
            "relevant_regulations": [],
            "compliance_status": "",
            "feedback": "",
            "final_output": "",
            "llm_provider": request.provider,
            # Credentials
            "api_key": request.api_key,
            "endpoint": request.endpoint,
            "aws_access_key": request.aws_access_key,
            "aws_secret_key": request.aws_secret_key,
            "aws_region": request.aws_region,
            "google_key": request.google_key,
            # Extras
            "azure_deployment": request.azure_deployment,
            "azure_api_version": request.azure_api_version,
            "aws_model_id": request.aws_model_id,
            "google_model": request.google_model
        }
        
        result = graph.invoke(initial_state)
        
        return ScanResponse(
            compliance_status=result.get("compliance_status", "UNKNOWN"),
            feedback=result.get("feedback", ""),
            final_output=result.get("final_output", ""),
            relevant_regulations=result.get("relevant_regulations", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_knowledge(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    source: str = Form(...)
):
    try:
        content = ""
        if file:
            content = (await file.read()).decode("utf-8")
        elif text:
            content = text
        else:
            raise HTTPException(status_code=400, detail="Either file or text must be provided.")
            
        add_regulation(content, source)
        return {"status": "success", "message": "Regulation added to Knowledge Base."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
