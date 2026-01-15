from typing import List, Dict

class ValidationTools:
    """
    Simulates an MCP Server providing external validation tools.
    In a real deployment, this would be a separate process communicating via stdio/HTTP.
    """
    
    @staticmethod
    def check_sanctions(name: str) -> List[str]:
        """Simulates a global sanctions list check."""
        # Simple simulation: names starting with "X" are sanctioned
        if name.upper().startswith("X") or "LADEN" in name.upper():
            return ["SDN List Hit: Specially Designated National", "Terrorist Watchlist Hit"]
        return []

    @staticmethod
    def verify_id_format(id_number: str, country: str) -> bool:
        """Simulates ID format validation logic."""
        if country == "US" and len(id_number) == 9: # SSN
            return True
        if country == "UK" and len(id_number) == 8: # NI
            return True
        # Default Fail for unknown formats in this mock
        return False

    @staticmethod
    def check_pep_list(name: str) -> bool:
        """Politically Exposed Person check."""
        if "PRESIDENT" in name.upper() or "MINISTER" in name.upper():
            return True
        return False
