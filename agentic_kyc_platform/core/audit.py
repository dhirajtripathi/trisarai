from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid

class AuditEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    action: str
    details: str
    tool_calls: Optional[List[Dict[str, Any]]] = None # To track verbatim inputs/outputs
    reasoning_trace: Optional[str] = None # Capture the "Chain of Thought"

class AuditLog(BaseModel):
    entries: List[AuditEntry] = []

    def add_entry(self, agent: str, action: str, details: str, reasoning: str = None, tool_usage: List[Dict] = None):
        """Append an immutable audit record."""
        entry = AuditEntry(
            agent_id=agent,
            action=action,
            details=details,
            reasoning_trace=reasoning,
            tool_calls=tool_usage
        )
        self.entries.append(entry)

    def to_markdown(self) -> str:
        """Export audit trail for human review."""
        md = "# KYC Audit Trail\n\n"
        for e in self.entries:
            md += f"### [{e.timestamp.isoformat()}] {e.agent_id}: {e.action}\n"
            if e.reasoning_trace:
                md += f"> **Reasoning**: {e.reasoning_trace}\n\n"
            md += f"**Details**: {e.details}\n\n"
            if e.tool_calls:
                md += "**Tool Activity**:\n```json\n" + str(e.tool_calls) + "\n```\n\n"
            md += "---\n"
        return md
