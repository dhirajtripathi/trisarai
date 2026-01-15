# User Guide: AI Digital Delivery Orchestrator (DDO)

## 1. Functional Overview
The **AI Digital Delivery Orchestrator (DDO)** is a comprehensive management system for modern software delivery. It solves the problem of "Agile Fragmentation" by unifying Strategy, Execution, and Governance into a single intelligent platform.

### Business Value
*   **Alignment**: Ensures that the code being written (Execution Layer) actually matches the business goals (Strategy Layer).
*   **Velocity**: AI agents handle the administrative burden—writing tickets, calculating WSJF, updating roadmaps—freeing humans to focus on creative work.
*   **Governance**: Automated "Gates" ensure that no project bypasses security or compliance checks.

### Key Capabilities
*   **6 Specialized Agents**:
    *   **Product Owner (PO)**: Drafts high-quality User Stories with Acceptance Criteria.
    *   **Scrum Master (SM)**: Monitors sprint health and detects impediments.
    *   **Product Manager (PMA)**: Translates business goals into quarterly roadmaps.
    *   **Project Manager (PROJMA)**: Forecasts delivery dates and manages risk registers.
    *   **Program Manager (PGMA)**: Visualizes cross-team dependencies and critical paths.
    *   **Portfolio Orchestrator (ORCH)**: Enforces corporate policy and compliance.

### System Workflow
```mermaid
graph TD
    Strat[Strategy Layer] -->|Goals| PMA[Product Manager]
    PMA -->|Roadmap| PGMA[Program Manager]
    PGMA -->|Dependencies| PO[Product Owner]
    
    PO -->|Stories| Team[Dev Team]
    Team -->|Metrics| SM[Scrum Master]
    
    SM & PROJMA -->|Status| ORCH[Orchestrator]
    ORCH -->>|Gate Decision| Release[Production Release]
```

## 2. Launching the Tool
*   **Direct URL**: `http://localhost:8506` (or accessed via Unified Portal).
*   **API Port**: `8006`

## 3. Step-by-Step Walkthrough

### A. The Product Owner (Planning)
1.  **Select Role**: Click "Product Owner" in the sidebar.
2.  **Input**: Enter a raw requirement, e.g., "We need to add Apple Pay to the checkout flow."
3.  **Generate**: Click **"Generate Stories"**.
4.  **Review**: The agent outputs detailed stories (e.g., "As a User, I want to select Apple Pay...").
    *   *WSJF Score*: Prioritization metric included.
    *   *Acceptance Criteria*: Gherkin syntax ready for QA.
5.  **Approve**: Click **"Approve"** to commit them to the mock backlog.

### B. The Scrum Master (Execution)
1.  **Select Role**: Click "Scrum Master".
2.  **Scan**: Click **"Scan Board"**.
3.  **Analysis**: The agent reads the Sprint Board state.
    *   *Metrics*: See Velocity and Cycle Time trends.
    *   *Anomalies*: "Alert: Ticket XYZ has been stuck in 'In Progress' for 5 days."
4.  **Action**: Click **"Escalate"** to notify the team.

### C. The Portfolio Orchestrator (Governance)
1.  **Select Role**: Click "Orchestrator".
2.  **Audit**: Click **"Run Compliance Check"**.
3.  **Gate Status**:
    *   If compliant: **"Governance Approved"** (Green Unlock Icon).
    *   If risky: **"Gate Locked"** (Red Lock Icon) with a list of violations (e.g., "Budget exceeded", "Security check missing").

## 4. Configuration
*   **Settings ⚙️**: Use the Settings tab to connect to your real Jira instance or switch LLM providers (Azure/AWS/Google).
