import asyncio
from agentic_kyc_platform.core.state import KYCCaseState, IngestedDocument, DocumentType
from agentic_kyc_platform.core.audit import AuditLog

def test_architecture_basics():
    print("--- Testing KYC Architecture Primitives ---")
    
    # 1. Initialize State
    case = KYCCaseState(
        case_id="CASE-123",
        customer_id="CUST-999"
    )
    print(f"✅ Case Initialized: {case.status}")
    
    # 2. Add Documents
    doc = IngestedDocument(filename="passport.pdf", file_path="/tmp/passport.pdf", doc_type=DocumentType.PASSPORT)
    case.documents.append(doc)
    print(f"✅ Document Added: {case.documents[0].filename}")
    
    # 3. Test Audit Logging
    case.audit_log.add_entry(
        agent="TestScript",
        action="INITIALIZE_CASE",
        details="Created case CUST-999",
        reasoning="User submitted application form"
    )
    
    assert len(case.audit_log.entries) == 1
    print("✅ Audit Log verified")
    
    print("\n--- Audit Trail Output ---")
    print(case.audit_log.to_markdown())

if __name__ == "__main__":
    test_architecture_basics()
