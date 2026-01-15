from typing import List, Dict, Any
import datetime
from .mcp_schema import (
    MCPEnvelope, RoleContext, TaskContext, DeliveryContext, TeamContext, GovernanceContext,
    StrategicContext, ResourceContext, DependencyContext, TemporalContext, 
    PortfolioContext, RiskContext, FinancialContext
)

# --- Mock Data ---
MOCK_BACKLOG = [
    {"id": "EPIC-101", "title": "Migrate Login to OAuth2", "status": "Proposed"},
    {"id": "STORY-205", "title": "Update React Components", "status": "Ready"},
]

MOCK_SPRINT_BOARD = [
    {"id": "TASK-501", "title": "DB Schema Sync", "status": "In Progress", "days_in_status": 1},
    {"id": "TASK-502", "title": "API Stress Test", "status": "Blocked", "days_in_status": 4}, # STALE TICKET
    {"id": "TASK-503", "title": "CSS Fixes", "status": "To Do", "days_in_status": 0},
]

class ContextCurator:
    def __init__(self):
        pass

    def build_po_context(self, objective: str) -> MCPEnvelope:
        """
        Builds the context for the Product Owner Agent.
        Aggregates Backlog data.
        """
        return MCPEnvelope(
            role=RoleContext(name="Product Owner Agent", authority="recommend"),
            task=TaskContext(
                objective=objective,
                constraints=["Sprint Capacity: 40 pts", "Strategic Theme: Security"]
            ),
            delivery=DeliveryContext(
                backlog_summary=f"Active Epics: {[i['title'] for i in MOCK_BACKLOG]}",
                prioritization={"model_name": "WSJF", "parameters": {"risk_weight": 0.5}}
            ),
            team=TeamContext(velocity=35, skills=["Backend", "Security"]),
            governance=GovernanceContext(human_approval_required=True, confidence_threshold=0.85)
        )

    def build_sm_context(self) -> MCPEnvelope:
        """
        Builds the context for the Scrum Master Agent.
        Aggregates Sprint Board flow metrics.
        """
        # Calculate Flow Metrics
        stale_tickets = [t['id'] for t in MOCK_SPRINT_BOARD if t['days_in_status'] > 3]
        
        return MCPEnvelope(
            role=RoleContext(name="Scrum Master Agent", authority="recommend"),
            task=TaskContext(objective="Optimize Sprint Flow", constraints=[]),
            delivery=DeliveryContext(
                flow_metrics={
                    "velocity": 35,
                    "cycle_time": "5 days",
                    "wip_limit": 5
                }
            ),
            team=TeamContext(
                velocity=35, 
                skills=["FullStack"],
                blockers=[f"Ticket {t} is stale (>3 days)" for t in stale_tickets]
            ),
            governance=GovernanceContext(human_approval_required=False, confidence_threshold=0.9)
        )

    def build_pma_context(self, goal: str) -> MCPEnvelope:
        role = RoleContext(name="Product Manager Agent", authority="recommend")
        task = TaskContext(objective=f"Generate Roadmap for: {goal}", constraints=["Must align with Q3 OKRs"])
        
        strategic = StrategicContext(
            business_goals=["Increase Enterprise Adoption", "Reduce Churn by 15%"],
            okrs=["Achieve $2M ARR", "NPS > 50"]
        )
        
        temporal = TemporalContext(planning_horizon="Next 2 Quarters")
        
        # Partially populated other contexts
        delivery = DeliveryContext(backlog_items=[], sprint_velocity=0)
        team = TeamContext(members=[], capacity=0)
        gov = GovernanceContext(human_approval_required=True, confidence_threshold=0.8)

        return MCPEnvelope(
            role=role, task=task, delivery=delivery, team=team, governance=gov,
            strategic=strategic, temporal=temporal
        )

    def build_projma_context(self) -> MCPEnvelope:
        role = RoleContext(name="Project Manager Agent", authority="recommend")
        task = TaskContext(objective="Forecast Q3 Delivery", constraints=["Fixed Release Date: Sept 30"])
        
        resource = ResourceContext(team_capacity=45, constraints=["Front-end dev on leave in August"])
        dependency = DependencyContext(cross_team_dependencies=["Wait for Auth Service v2 API"])
        temporal = TemporalContext(planning_horizon="Q3", milestones={"Code Freeze": "Sept 15", "Release": "Sept 30"})
        
        # Simulate backlog for forecasting
        delivery = DeliveryContext(
            backlog_items=[f"Task-{i}" for i in range(1, 15)],
            sprint_velocity=40
        )
        team = TeamContext(members=["Alice", "Bob"], capacity=45)
        gov = GovernanceContext(human_approval_required=False, confidence_threshold=0.9)

        return MCPEnvelope(
            role=role, task=task, delivery=delivery, team=team, governance=gov,
            resource=resource, dependency=dependency, temporal=temporal
        )

    def build_pgma_context(self) -> MCPEnvelope:
        role = RoleContext(name="Program Manager Agent", authority="recommend")
        task = TaskContext(objective="Assess Program Health", constraints=[])
        
        portfolio = PortfolioContext(
            active_programs=["Mobile App Refresh", "Legacy Migration", "AI Platform"],
            objectives=["Modernization", "Efficiency"]
        )
        
        # Simulate cross-team dependencies
        dependency = DependencyContext(
            cross_team_dependencies=["Mobile Team blocked by Legacy API Team", "AI Team waiting for Cloud Ops"]
        )
        
        risk = RiskContext(
            systemic_risks=["Backend Bottleneck identified across 2 programs"],
            risk_heatmap={"Mobile App Refresh": "HIGH", "Legacy Migration": "MEDIUM", "AI Platform": "LOW"}
        )

        return MCPEnvelope(
            role=role, task=task, delivery=DeliveryContext(backlog_items=[], sprint_velocity=0), 
            team=TeamContext(members=[], capacity=0), governance=GovernanceContext(human_approval_required=True),
            portfolio=portfolio, dependency=dependency, risk=risk
        )

    def build_orch_context(self) -> MCPEnvelope:
        role = RoleContext(name="Portfolio Orchestrator", authority="execute_with_constraints")
        task = TaskContext(objective="Enforce Governance Policies", constraints=["No budget overruns"])
        
        portfolio = PortfolioContext(
            active_programs=["Mobile App Refresh", "Legacy Migration", "AI Platform"],
            policies=["Budget > $50k requires EVP Approval", "Security Audit mandatory for AI"],
        )
        
        financial = FinancialContext(
            budget_burn={"Mobile App Refresh": 0.85, "Legacy Migration": 1.1, "AI Platform": 0.4},
            cost_centers=["Eng-Mobile", "Eng-Backend", "R&D"]
        )

        risk = RiskContext(
            systemic_risks=["Backend Bottleneck identified across 2 programs"],
            risk_heatmap={"Mobile App Refresh": "HIGH", "Legacy Migration": "MEDIUM", "AI Platform": "LOW"}
        )
        
        return MCPEnvelope(
            role=role, task=task, delivery=DeliveryContext(backlog_items=[], sprint_velocity=0), 
            team=TeamContext(members=[], capacity=0), governance=GovernanceContext(human_approval_required=True, confidence_threshold=0.9),
            portfolio=portfolio, financial=financial, risk=risk
        )
