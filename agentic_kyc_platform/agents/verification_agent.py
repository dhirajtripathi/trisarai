from ..core.base_agent import BaseAgent
from ..core.state import KYCCaseState, CaseStatus, VerificationCheck
from ..mcp_servers.validation_tools.mock_server import ValidationTools

class VerificationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="VerificationAgent",
            role_description="Validates identity against external databases."
        )

    async def process(self, state: KYCCaseState) -> KYCCaseState:
        # Pre-condition check
        if not state.extracted_data:
            self.log_action(state, "SKIP", "No extracted data available to verify")
            return state

        state.status = CaseStatus.VERIFYING
        data = state.extracted_data

        # 1. Sanctions Check
        sanctions = ValidationTools.check_sanctions(data.full_name)
        sanction_passed = len(sanctions) == 0
        state.verification_checks.append(VerificationCheck(
            check_name="Global Sanctions List",
            passed=sanction_passed,
            details=f"Hits: {sanctions}" if not sanction_passed else "No hits found"
        ))
        
        # 2. ID Format Check
        id_valid = ValidationTools.verify_id_format(data.id_number, data.nationality)
        state.verification_checks.append(VerificationCheck(
            check_name="ID Syntax Validation",
            passed=id_valid,
            details=f"ID {data.id_number} format valid for {data.nationality}" if id_valid else "Invalid format"
        ))

        # Log overarching result
        self.log_action(
            state,
            "RUN_CHECKS",
            f"Completed {len(state.verification_checks)} checks",
            reasoning=f"Sanctions={'Pass' if sanction_passed else 'FAIL'}, ID={'Pass' if id_valid else 'FAIL'}",
            tools=[
                {"tool": "check_sanctions", "input": data.full_name, "output": sanctions},
                {"tool": "verify_id_format", "input": {"id": data.id_number, "country": data.nationality}, "output": id_valid}
            ]
        )
        
        state.status = CaseStatus.REVIEW_CHECKS
        return state
