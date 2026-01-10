import re

def validate_accusation(agent_output: str) -> tuple[bool, str]:
    """
    Guardrail to ensure the agent does not make unsupported accusations.
    Returns (is_safe, reason).
    """
    
    # 1. Check for biased language
    biased_terms = ["liar", "thief", "criminal", "scammer", "definitely fraud"]
    for term in biased_terms:
        if term in agent_output.lower():
            return False, f"Output contains biased/unprofessional language: '{term}'. Please rephrase objectively."

    # 2. Check for "Hallucinated" High Confidence without Evidence
    # If agent says "High Risk" but mentions "No evidence found", that's a hallucination or logic error.
    if "high risk" in agent_output.lower() and "no evidence found" in agent_output.lower():
        return False, "Logical Error: Claim flagged as High Risk but text says no evidence found."

    return True, "Output passed safety checks."
