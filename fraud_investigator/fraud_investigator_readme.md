# Agentic Fraud Investigator
**Usecase Name**: `fraud_investigator`

## 1. Functional Overview
The **Fraud Investigator Agent** is an autonomous "Special Investigations Unit" (SIU) dashboard. It detects anomalies in transaction patterns, investigates "Ghost Broking" rings, and flags suspicious claims for human review.

### Key Features
*   **Anomaly Detection**: Monitors stream of transactions for statistical outliers.
*   **Network Analysis**: Detects linked entities (e.g., same IP used for 50 distinct policy applications).
*   **Auto-Triage**: Classifies alerts as "False Positive", "Review Needed", or "High Risk".
*   **Investigative Report**: Generates a summary dossier for the human investigator.

## 2. Technical Architecture (LangGraph)
Uses **LangGraph** to model the investigation lifecycle.

### Workflow Nodes (`graph.py`)
1.  **Monitor Node**:
    *   Ingests transaction stream.
    *   Applies statistical thresholds (Z-Score).
2.  **Investigation Node**:
    *   Triggered if Risk > Threshold.
    *   Queries external databases (Mock/SQL) to build a profile.
    *   LLM Reasoning: "Is this behavior consistent with known fraud typologies?"
3.  **Reporting Node**:
    *   Compiles evidence into a structured JSON/PDF report.

## 3. Implementation Steps

### Prerequisites
*   Python 3.10+
*   Streamlit

### Setup & Run
1.  **Navigate**: `cd fraud_investigator`
2.  **Install**: `pip install -r requirements.txt`
3.  **Run**: `streamlit run app.py`

### Testing
Use the sidebar to simulate a "Ghost Broker" attack pattern (Rapid sequence of policies from one device). Watch the Agent trigger an investigation loop.

## 4. Context Engineering
*   **Typology Injection**: The System Prompt includes a library of known fraud schemes (e.g., "Build-up", "Jump-in").
*   **Chain of Thought**: The agent is forced to output its hypothesis *before* its verdict to ensure explainability in court.
