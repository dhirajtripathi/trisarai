# Agentic KYC Platform
**Usecase Name**: `agentic_kyc_platform`

## 1. Functional Overview
The **Agentic KYC Platform** transforms Identity Verification from a manual back-office task into an autonomous Multi-Agent collaboration. It orchestrates specialized agents to analyze documents, assess risk, and ensure regulatory compliance.

### Key Features
*   **Multi-Agent Swarm**: Specialized agents (Document Analyst, Risk Officer, Compliance Bot) working in parallel.
*   **Document Parsing**: OCR extraction from ID cards and Utility Bills.
*   **Risk Scoring**: Real-time sanctions screening and PEP (Politically Exposed Person) checks.
*   **Audit Trail**: Full decision lineage explanation for regulators.

## 2. Technical Architecture
The system uses a **Hub-and-Spoke** or **Hierarchical** agent pattern.

### Specialized Agents (`/agents`)
1.  **Doc Analysis Agent**:
    *   Role: extract structured data from unstructured images/PDFs.
    *   Tool: `ocr_extraction`.
2.  **Risk Agent**:
    *   Role: Calculate risk score (0-100).
    *   tool: `sanctions_check`.
3.  **Compliance Agent**:
    *   Role: Final approval based on Risk Score + Doc Validity.
    *   Result: `approve` | `reject` | `manual_review`.

### MCP Servers
The agents rely on two helper MCP servers:
*   `validation_tools`: Provides `verify_id_format(id)` and `check_sanctions_list(name)`.
*   `policy_rag`: Provides "KYC Policy 2024" context to the Compliance Agent.

## 3. Implementation Steps

### Setup & Run
1.  **Navigate**: `cd agentic_kyc_platform`
2.  **Install**: `pip install -r requirements.txt`
3.  **Run UI**:
    *   `cd ../kyc_dashboard_ui`
    *   `npm install && npm run dev`
    *   Access Dashboard at `http://localhost:5175`.

### API Usage
The platform exposes a FastAPI endpoint for the UI:
```bash
POST /api/kyc/onboard
{
  "name": "John Doe",
  "id_doc": "base64...",
  "address_proof": "base64..."
}
```

## 4. Context Engineering
*   **Role-Based Prompts**: Each agent has a distinct "Persona" in its system prompt (e.g., "You are a conservative Risk Officer...").
*   **Handoffs**: The system demonstrates how to pass the "Case File" (Context) from one agent to the next without losing information.
