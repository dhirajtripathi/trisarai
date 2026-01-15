from ..core.base_agent import BaseAgent
from ..core.state import KYCCaseState, CaseStatus

class ComplianceReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ComplianceReviewAgent",
            role_description="Makes final approval/rejection decision based on full case context."
        )

    async def process(self, state: KYCCaseState) -> KYCCaseState:
        state.status = CaseStatus.GENERATING_DECISION
        
        if not state.risk_assessment:
            self.log_action(state, "ERROR", "Cannot decide without risk assessment")
            return state

        risk = state.risk_assessment
        
        # Decision Logic (Proposal)
        if risk.level == "HIGH":
            decision = CaseStatus.REJECTED
            reason = f"Rejected due to HIGH risk score ({risk.score}). Critical factors found."
        elif risk.level == "MEDIUM":
            decision = CaseStatus.REVIEW_DECISION # Manual review implicitly
            reason = f"Flagged for human review. Risk score {risk.score} requires analyst sign-off."
        else:
            decision = CaseStatus.APPROVED
            reason = "Automated Approval. Low risk profile and all checks passed."

        state.final_decision_reason = reason
        state.status = CaseStatus.REVIEW_DECISION # Human always confirms final

        self.log_action(
            state,
            "PROPOSE_DECISION",
            f"Proposed: {decision}",
            reasoning=state.final_decision_reason
        )
        
        return state
