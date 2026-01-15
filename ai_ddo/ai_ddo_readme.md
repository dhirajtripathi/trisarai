# AI DDO (Digital Delivery Orchestrator)
**Usecase Name**: `ai_ddo`

## 1. Functional Overview
**AI DDO** is a multi-agent platform designed to orchestrate the entire software delivery lifecycle. It acts as an "AI Office of the CIO," providing specialized agents for every role in an Agile organization—from Product Owners refining backlogs to Portfolio Orchestrators enforcing governance.

### Key Features
*   **Role-Based Concierge**: 6 distinct personas (PO, Scrum Master, Project Manager, Program Manager, Product Manager, Orchestrator).
*   **Context Engineering**: Generates high-quality User Stories, Roadmaps, and Risk Assessments based on minimal input.
*   **Governance Gate**: Automates compliance checks before releases.
*   **Cross-Team Dependency Scanning**: Detects blockers across the program portfolio.

## 2. Technical Architecture
The system uses a Micro-Frontend architecture with a shared React UI (`ui/`) and a Python backend (`api.py`) that routes requests to specialized agent workflows.

### Components
1.  **UI Layer**: React + TailwindCSS dashboard with role-switching capabilities.
2.  **Agent Layer (`agents/`)**:
    *   `po_agent`: Generates user stories (WSJF, Acceptance Criteria).
    *   `sm_agent`: Analyzes sprint velocity and flow efficiency.
    *   `pm_agent`: Generates strategic roadmaps.
    *   `orch_agent`: Validates compliance against policy docs.
3.  **Config Store**: Manages LLM and Jira credentials dynamically.

## 3. Implementation Steps

### Prerequisites
*   Python 3.11+
*   Node.js 18+
*   LLM API Key (Azure/AWS/Google)

### Setup & Run
1.  **Navigate**: `cd ai_ddo`
2.  **Install**: `pip install -r requirements.txt`
3.  **Run API**: `python api.py`
4.  **Run UI**: `cd ui && npm install && npm run dev`

## 4. Agentic Concepts
*   **Hierarchical Planning**: Strategy (PM) -> Roadmap (PgM) -> Backlog (PO) -> Execution (SM).
*   **Active Governance**: The Orchestrator agent can "Lock the Gate," preventing deployment if risks are too high.
