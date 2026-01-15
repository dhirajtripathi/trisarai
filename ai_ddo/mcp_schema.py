from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- 1. Role Context ---
class RoleContext(BaseModel):
    name: str = Field(..., description="Name of the agent role (e.g., Product Owner Agent)")
    authority: str = Field(..., description="Authority level: 'recommend', 'act', 'approve'")

# --- 2. Task Context ---
class TaskContext(BaseModel):
    objective: str = Field(..., description="Primary goal of the current task")
    constraints: List[str] = Field(default_factory=list, description="Hard constraints (e.g. Budget, Capacity)")
    deadline: Optional[str] = None

# --- 3. Delivery Context ---
class PrioritizationModel(BaseModel):
    model_name: str = "WSJF"
    parameters: Dict[str, Any] = {}

class DeliveryContext(BaseModel):
    backlog_summary: Optional[str] = None
    backlog_items: List[str] = [] 
    flow_metrics: Optional[Dict[str, Any]] = None # velocity, cycle_time
    prioritization: Optional[PrioritizationModel] = None

# --- 4. Team Context ---
class TeamContext(BaseModel):
    velocity: int = 0
    skills: List[str] = []
    blockers: List[str] = []

# --- 5. Governance Context ---
class GovernanceContext(BaseModel):
    human_approval_required: bool = True
    confidence_threshold: float = 0.85
    policy_enforcement: List[str] = []

# --- ROOT: MCP Envelope ---
class StrategicContext(BaseModel):
    business_goals: List[str] = Field(..., description="High-level business objectives")
    okrs: List[str] = Field(..., description="Key Results to measure success")

class ResourceContext(BaseModel):
    team_capacity: int = Field(..., description="Aggregate team velocity or capacity units")
    constraints: List[str] = Field(default_factory=list, description="Resource hard constraints")

class DependencyContext(BaseModel):
    external_dependencies: List[str] = Field(default_factory=list, description="Upstream/Downstream dependencies")
    cross_team_dependencies: List[str] = Field(default_factory=list, description="Dependencies on other squads")

class TemporalContext(BaseModel):
    planning_horizon: str = Field(..., description="Time period for the context (e.g. 'Q3')")
    milestones: Dict[str, str] = Field(default_factory=dict, description="Key delivery dates")

# --- Phase 3 Additions ---
class PortfolioContext(BaseModel):
    active_programs: List[str] = Field(..., description="List of active programs or initiatives")
    objectives: List[str] = Field(default_factory=list, description="Strategic themes for the portfolio")
    policies: List[str] = Field(default_factory=list, description="Governance rules active")

class FinancialContext(BaseModel):
    budget_burn: Dict[str, float] = Field(default_factory=dict, description="Burn rate per program")
    cost_centers: List[str] = Field(default_factory=list, description="Active cost centers")

class RiskContext(BaseModel):
    systemic_risks: List[str] = Field(default_factory=list, description="Aggregated high-level risks")
    risk_heatmap: Dict[str, str] = Field(default_factory=dict, description="Risk level per program (Low/Med/High)")

class MCPEnvelope(BaseModel):
    role: RoleContext
    task: TaskContext
    delivery: DeliveryContext
    team: TeamContext
    governance: GovernanceContext
    
    # Phase 2 Additions
    strategic: Optional[StrategicContext] = None
    resource: Optional[ResourceContext] = None
    dependency: Optional[DependencyContext] = None
    temporal: Optional[TemporalContext] = None
    
    # Phase 3 Additions
    portfolio: Optional[PortfolioContext] = None
    financial: Optional[FinancialContext] = None
    risk: Optional[RiskContext] = None
    
    memory: Dict[str, Any] = Field(default_factory=dict, description="Short-term Agent Memory")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": {"name": "Product Owner Agent", "authority": "recommend"},
                "task": {"objective": "Refine Backlog", "constraints": ["Capacity=40"]},
                "delivery": {"backlog_summary": "5 Epics awaiting refinement"},
                "team": {"velocity": 38, "skills": ["React", "Python"]},
                "governance": {"human_approval_required": True}
            }
        }
