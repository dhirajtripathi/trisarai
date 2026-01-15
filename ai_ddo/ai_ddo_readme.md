# AI DDO (Due Diligence Operations)
**Usecase Name**: `ai_ddo`

## 1. Functional Overview
**AI DDO (Digital Due Diligence Operations)** is a heavy-duty agentic platform designed for M&A (Mergers & Acquisitions) and complex Data Operations. It ingests "Data Rooms" (massive sets of unstructured financial/legal docs) and performs autonomous due diligence.

### Key Features
*   **Context Curation**: Intelligently groups 1000s of pages into "Semantic Clusters".
*   **Multi-Agent Swarm**: Specialized agents for "Legal Risk", "Financial Audit", and "Tech Stack Assessment".
*   **Red Flag Detection**: Autonomously flags "Change of Control" clauses or "Pending Litigation".

## 2. Technical Architecture (MCP & Context Layers)
This is the most advanced Context Engineering implementation in the suite.

### Components
1.  **Context Curator (`context_curator.py`)**:
    *   Uses **Hierarchical Summarization**. Segments docs -> Summaries -> Meta-Summaries.
    *   Allows the LLM to navigate a 10GB Data Room without exploding the context window.
2.  **MCP Schema (`mcp_schema.py`)**:
    *   Exposes the "Data Room" as a searchable tool resource.
    *   Standardizes query interfaces for the sub-agents.
3.  **Agent Swarm (`/agents`)**:
    *   Independent processes analyzing different aspects of the same data set concurrently.

## 3. Implementation Steps

### Prerequisites
*   Python 3.10+
*   Vector Store (Chroma)

### Setup & Run
1.  **Navigate**: `cd ai_ddo`
2.  **Install**: `pip install -r requirements.txt`
3.  **Run API**: `python api.py`
4.  **Run UI**: `cd ui && npm start` (or similar)

## 4. Agentic Concepts
*   **Reflective Search**: If an agent can't find an answer in Summary Level 1, it autonomously decides to "drill down" to Level 2 (Full Text) for specific chapters.
*   **Cross-Validation**: The "Legal Agent" and "Financial Agent" share findings to detect discrepancies (e.g., Legal says "No debt" but Finance sees "Loan Payments").
