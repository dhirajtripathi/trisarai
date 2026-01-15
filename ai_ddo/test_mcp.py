from mcp_schema import MCPEnvelope
import json

sample_data = {
    "role": {"name": "Product Owner Agent", "authority": "recommend"},
    "task": {"objective": "Refine Backlog", "constraints": ["Capacity=40"]},
    "delivery": {
        "backlog_summary": "5 Epics awaiting refinement",
        "flow_metrics": {"velocity": 40} 
    },
    "team": {"velocity": 38, "skills": ["React", "Python"]},
    "governance": {"human_approval_required": True, "confidence_threshold": 0.9}
}

try:
    envelope = MCPEnvelope(**sample_data)
    print("✅ MCP Validation Success!")
    print(envelope.model_dump_json(indent=2))
except Exception as e:
    print(f"❌ Validation Failed: {e}")
