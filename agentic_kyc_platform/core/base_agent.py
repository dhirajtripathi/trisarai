from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .state import KYCCaseState
from .audit import AuditLog

class BaseAgent(ABC):
    def __init__(self, name: str, role_description: str):
        self.name = name
        self.role_description = role_description
        
    @abstractmethod
    async def process(self, state: KYCCaseState) -> KYCCaseState:
        """
        Main entry point. Receives state, performs work, updates state, returns state.
        MUST log to state.audit_log
        """
        pass

    def log_action(self, state: KYCCaseState, action: str, details: str, reasoning: str = None, tools: List[Dict] = None):
        """Helper to append to the case's audit log."""
        state.audit_log.add_entry(
            agent=self.name,
            action=action,
            details=details,
            reasoning=reasoning,
            tool_usage=tools
        )
        print(f"[{self.name}] {action}: {details}")

    async def call_dummy_mcp_tool(self, tool_name: str, args: Dict) -> Any:
        # Placeholder for real MCP client call
        # In this minimal implementaton, we mock the tool calls or implement them directly for now
        return {"result": "success", "mock_data": "simulated"}
