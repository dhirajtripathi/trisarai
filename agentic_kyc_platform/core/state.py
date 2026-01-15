from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from .audit import AuditLog

class CaseStatus(str, Enum):
    NEW = "NEW"
    ANALYZING_DOCS = "ANALYZING_DOCS"
    REVIEW_DOCS = "REVIEW_DOCS"           # HITL Gate 1
    VERIFYING = "VERIFYING"
    REVIEW_CHECKS = "REVIEW_CHECKS"       # HITL Gate 2
    ASSESSING_RISK = "ASSESSING_RISK"
    REVIEW_RISK = "REVIEW_RISK"           # HITL Gate 3
    GENERATING_DECISION = "GENERATING_DECISION"
    REVIEW_DECISION = "REVIEW_DECISION"   # HITL Gate 4
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"

class DocumentType(str, Enum):
    PASSPORT = "PASSPORT"
    DRIVERS_LICENSE = "DRIVERS_LICENSE"
    UTILITY_BILL = "UTILITY_BILL"
    UNKNOWN = "UNKNOWN"

class IngestedDocument(BaseModel):
    filename: str
    file_path: str
    doc_type: DocumentType = DocumentType.UNKNOWN
    # In a real system, we'd store a hash here too

class ExtractedData(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[str] = None
    id_number: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    confidence_score: float = 0.0

class VerificationCheck(BaseModel):
    check_name: str # e.g. "Sanctions Check"
    passed: bool
    details: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class RiskAssessment(BaseModel):
    score: float # 0-100
    level: str # LOW, MEDIUM, HIGH
    factors: List[str]

class KYCCaseState(BaseModel):
    """
    The Single Source of Truth for a KYC Case.
    Passed between agents to maintain state.
    """
    case_id: str
    customer_id: str
    status: CaseStatus = CaseStatus.NEW
    
    # 1. Documents (Input)
    documents: List[IngestedDocument] = []
    
    # 2. Analysis (Step 1)
    extracted_data: Optional[ExtractedData] = None
    
    # 3. Verification (Step 2)
    verification_checks: List[VerificationCheck] = []
    
    # 4. Risk (Step 3)
    risk_assessment: Optional[RiskAssessment] = None
    
    # 5. Final Decision
    final_decision_reason: Optional[str] = None
    
    # Audit
    audit_log: AuditLog = Field(default_factory=AuditLog)
