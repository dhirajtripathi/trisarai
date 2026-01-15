from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
import asyncio
import uuid
import os
import sqlite3
import json
from contextlib import asynccontextmanager

from agentic_kyc_platform.core.state import KYCCaseState, IngestedDocument, DocumentType, CaseStatus
from agentic_kyc_platform.agents.doc_analysis_agent import DocumentAnalysisAgent
from agentic_kyc_platform.agents.verification_agent import VerificationAgent
from agentic_kyc_platform.agents.risk_agent import RiskAssessmentAgent
from agentic_kyc_platform.agents.compliance_agent import ComplianceReviewAgent

# DB Setup
DB_PATH = "./data/kyc.db"
os.makedirs("./data/uploads", exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                customer_id TEXT,
                status TEXT,
                state_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def save_case(case: KYCCaseState):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO cases (case_id, customer_id, status, state_json) VALUES (?, ?, ?, ?)",
            (case.case_id, case.customer_id, case.status.value, case.model_dump_json())
        )

def load_case(case_id: str) -> KYCCaseState:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT state_json FROM cases WHERE case_id = ?", (case_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return KYCCaseState.model_validate_json(row[0])

def list_cases_from_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT case_id, customer_id, status, created_at FROM cases ORDER BY created_at DESC")
        return [
            {"case_id": r[0], "customer_id": r[1], "status": r[2], "created_at": r[3]}
            for r in cursor.fetchall()
        ]

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Agentic KYC Platform API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Workflow Drivers ---

async def run_stage_analysis(case_id: str):
    case = load_case(case_id)
    if not case: return
    
    # Run Agent
    agent = DocumentAnalysisAgent()
    print(f"[{case_id}] Running {agent.name}...")
    case = await agent.process(case)
    save_case(case)

async def run_stage_verification(case_id: str):
    case = load_case(case_id)
    if not case: return
    
    agent = VerificationAgent()
    print(f"[{case_id}] Running {agent.name}...")
    case = await agent.process(case)
    save_case(case)

async def run_stage_risk(case_id: str):
    case = load_case(case_id)
    if not case: return
    
    agent = RiskAssessmentAgent()
    print(f"[{case_id}] Running {agent.name}...")
    case = await agent.process(case)
    save_case(case)

async def run_stage_decision(case_id: str):
    case = load_case(case_id)
    if not case: return
    
    agent = ComplianceReviewAgent()
    print(f"[{case_id}] Running {agent.name}...")
    case = await agent.process(case)
    save_case(case)

# --- Endpoints ---

@app.post("/cases")
async def create_case():
    case_id = str(uuid.uuid4())[:8]
    new_case = KYCCaseState(
        case_id=case_id,
        customer_id=f"CUST-{uuid.uuid4().hex[:6].upper()}"
    )
    save_case(new_case)
    return {"case_id": case_id, "message": "Case initialized"}

@app.post("/cases/{case_id}/upload")
async def upload_document(case_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    case = load_case(case_id)
    if not case: raise HTTPException(404, "Case not found")
    
    # Save file
    file_path = os.path.abspath(os.path.join("./data/uploads", f"{case_id}_{file.filename}"))
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    # Update State
    case.documents.append(IngestedDocument(
        filename=file.filename,
        file_path=file_path,
        doc_type=DocumentType.UNKNOWN
    ))
    save_case(case)
    
    # Trigger Analysis immediately upon upload
    background_tasks.add_task(run_stage_analysis, case_id)
    
    return {"message": "File uploaded, analysis started"}

@app.post("/cases/{case_id}/actions/approve_doc")
async def approve_doc(case_id: str, background_tasks: BackgroundTasks, data: Dict[str, Any] = Body(...)):
    """User edits/confirms extracted data."""
    case = load_case(case_id)
    if not case: raise HTTPException(404, "Case not found")
    
    # Update with user edits
    if "extracted_data" in data and case.extracted_data:
        # Simple merge or replace logic
        updated = data["extracted_data"]
        case.extracted_data.full_name = updated.get("full_name", case.extracted_data.full_name)
        case.extracted_data.id_number = updated.get("id_number", case.extracted_data.id_number)
        
    case.audit_log.add_entry("HUMAN_REVIEWER", "APPROVE_DOCS", "User validated data extraction.")
    save_case(case)
    
    # Trigger Next Stage
    background_tasks.add_task(run_stage_verification, case_id)
    return {"status": "Verification Started"}

@app.post("/cases/{case_id}/actions/approve_checks")
async def approve_checks(case_id: str, background_tasks: BackgroundTasks):
    """User confirms verification checks."""
    case = load_case(case_id)
    case.audit_log.add_entry("HUMAN_REVIEWER", "APPROVE_CHECKS", "User validated verification checks.")
    save_case(case)
    
    background_tasks.add_task(run_stage_risk, case_id)
    return {"status": "Risk Assessment Started"}

@app.post("/cases/{case_id}/actions/approve_risk")
async def approve_risk(case_id: str, background_tasks: BackgroundTasks):
    """User confirms risk score."""
    case = load_case(case_id)
    case.audit_log.add_entry("HUMAN_REVIEWER", "APPROVE_RISK", "User accepted risk scoring.")
    save_case(case)
    
    background_tasks.add_task(run_stage_decision, case_id)
    return {"status": "Decision Generation Started"}

@app.post("/cases/{case_id}/actions/finalize")
async def finalize_decision(case_id: str, decision: str = Body(..., embed=True)):
    """User makes final decision (Approve/Reject)."""
    case = load_case(case_id)
    
    case.status = CaseStatus.APPROVED if decision == "APPROVED" else CaseStatus.REJECTED
    case.audit_log.add_entry("HUMAN_REVIEWER", "FINAL_DECISION", f"User manually finalized case as {decision}")
    save_case(case)
    
    return {"status": "Case Closed"}

@app.get("/cases")
async def list_cases_endpoint():
    return list_cases_from_db()

@app.get("/cases/{case_id}")
async def get_case_endpoint(case_id: str):
    c = load_case(case_id)
    if not c: raise HTTPException(404, "Case not found")
    return c

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
