from pydantic import BaseModel, Field
from typing import List, Optional

class CustomerProfile(BaseModel):
    id: str
    name: str
    age: int
    existing_policies: List[str]  # e.g., ["Auto", "Renters"]
    annual_premium: float
    risk_score: int # 1-100

class LifeEvent(BaseModel):
    event_type: str # "Marriage", "New Home", "New Child", "New Car"
    description: str
    timestamp: str

class EndorsementProposal(BaseModel):
    policy_type: str # "Homeowners", "Life", "Auto"
    recommended_action: str # "Add Policy", "Increase Coverage"
    premium_change: float # +$500
    reasoning: str
    new_total_premium: float
