from ..core.base_agent import BaseAgent
from ..core.state import KYCCaseState, CaseStatus, RiskAssessment

class RiskAssessmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="RiskAssessmentAgent",
            role_description="Calculates risk profile based on verification results."
        )

    async def process(self, state: KYCCaseState) -> KYCCaseState:
        state.status = CaseStatus.ASSESSING_RISK
        
        score = 0
        factors = []
        
        # Analysis Logic
        for check in state.verification_checks:
            if not check.passed:
                if "Sanctions" in check.check_name:
                    score += 100
                    factors.append("CRITICAL: Sanctions Hit")
                elif "ID Syntax" in check.check_name:
                    score += 20
                    factors.append("WARNING: ID Syntax Invalid")
            else:
                factors.append(f"PASS: {check.check_name}")

        # Nationality Risk (Mock)
        if state.extracted_data and state.extracted_data.nationality in ["HighRiskCountry"]:
            score += 30
            factors.append("RISK: High Risk Jurisdiction")

        # Determine Level
        level = "LOW"
        if score >= 80:
            level = "HIGH"
        elif score >= 20:
            level = "MEDIUM"

        state.risk_assessment = RiskAssessment(
            score=min(score, 100),
            level=level,
            factors=factors
        )

        self.log_action(
            state,
            "CALCULATE_RISK",
            f"Risk Level: {level} (Score: {score})",
            reasoning=f"Factors: {', '.join(factors)}"
        )
        
        state.status = CaseStatus.REVIEW_RISK
        return state
