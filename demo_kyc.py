import asyncio
from agentic_kyc_platform.core.state import KYCCaseState, IngestedDocument, DocumentType
from agentic_kyc_platform.agents.doc_analysis_agent import DocumentAnalysisAgent
from agentic_kyc_platform.agents.verification_agent import VerificationAgent
from agentic_kyc_platform.agents.risk_agent import RiskAssessmentAgent
from agentic_kyc_platform.agents.compliance_agent import ComplianceReviewAgent

async def run_kyc_pipeline():
    print("🚀 Starting Agentic KYC Pipeline...\n")

    # 1. Initialize Case
    case = KYCCaseState(case_id="CASE-2024-001", customer_id="CUST-555")
    case.documents.append(IngestedDocument(
        filename="john_doe_passport.jpg", 
        file_path="/tmp/john_doe_passport.jpg", 
        doc_type=DocumentType.PASSPORT
    ))

    # 2. Define Agent Swarm
    agents = [
        DocumentAnalysisAgent(),
        VerificationAgent(),
        RiskAssessmentAgent(),
        ComplianceReviewAgent()
    ]

    # 3. Execution Loop
    for agent in agents:
        print(f"🤖 Handoff to {agent.name}...")
        case = await agent.process(case)
        print(f"   Current Status: {case.status.value}\n")

    # 4. Final Platform Output
    print("--- 🏁 Pipeline Complete ---")
    print(f"Final Decision: {case.status.value}")
    if case.final_decision_reason:
        print(f"Reason: {case.final_decision_reason}")
    
    print("\n--- 📜 Audit Trail (Regulatory Report) ---")
    print(case.audit_log.to_markdown())

if __name__ == "__main__":
    asyncio.run(run_kyc_pipeline())
