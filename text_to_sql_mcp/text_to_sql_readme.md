# Text-to-SQL Agentic Platform
**Usecase Name**: `text_to_sql_mcp`

## 1. Functional Overview
The **Text-to-SQL Platform** empowers business analysts to interact with enterprise databases using natural language. Unlike simple query generators, this is a **safe, agentic system** that understands business context, enforces security guardrails, and provides explainable insights.

### Key Features
*   **Natural Language Querying**: "Show me active users" -> `SELECT * FROM users WHERE status = 'active'`.
*   **Multi-Database Support**: Connects to PostgreSQL, MySQL, SQLite, and NoSQL (MongoDB mocks).
*   **Explainability**: Every query comes with a step-by-step "Thinking Process" and Confidence Score.
*   **Interactive Visualization**: Generates Mermaid.js Entity-Relationship (ER) diagrams on the fly.
*   **Unified Portal**: Integrated with the Data Intelligence Dashboard.

## 2. Technical Architecture (MCP & Agentic AI)
The system is built on the **Model Context Protocol (MCP)**, treating the LLM not just as a text generator but as a tool-using agent.

### Core Components
1.  **MCP Server (`FastAPI`)**:
    *   Acts as the central "Brain".
    *   Exposes tools: `generate_query`, `execute_query`, `get_schema`, `get_er_diagram`.
    *   Manages connections via `SQLAlchemy`.
2.  **Context Engine (`SchemaManager`)**:
    *   **Enrichment**: Injects business descriptions (e.g., "active means login < 30 days") into the prompt.
    *   **Schema Pruning**: Sends only relevant tables to the LLM context window.
3.  **Agentic "Query Guard" (Safety Layer)**:
    *   Parses generated SQL *before* execution.
    *   **Rules**: Read-Only enforcement (No INSERT/DROP), Limit constraints, Access Control.
4.  **Universal LLM Service (`LiteLLM`)**:
    *   Supports dynamic switching between OpenAI, Azure, AWS Bedrock, and Google Gemini.
    *   Standardizes prompts and response parsing.

## 3. Implementation Steps

### Prerequisites
*   Python 3.10+
*   Node.js (for UI)
*   Database (Postgres/MySQL) or use embedded SQLite.

### Backend Setup
1.  **Install Dependencies**:
    ```bash
    pip install fastapi uvicorn sqlalchemy litellm psycopg2-binary
    ```
2.  **Configure Environment**:
    Create `.env`:
    ```ini
    LLM_MODEL=azure/gpt-4
    AZURE_API_KEY=...
    DATABASE_URL=postgresql://user:pass@localhost:5432/db
    ```
3.  **Run Server**:
    ```bash
    python -m text_to_sql_mcp.main
    ```

### Frontend Setup
1.  **Install**: `cd text_to_sql_ui && npm install`
2.  **Run**: `npm run dev`
3.  **Access**: `http://localhost:5173`

## 4. Context Engineering & Prompts
To ensure high accuracy, we use a **Schema-Aware System Prompt**:

```text
You are an expert Data Analyst.
CONTEXT: {JSON Schema with Descriptions}
RULES:
1. Use ONLY provided tables.
2. If "Active User", use `status='active'`.
3. Return Read-Only JSON.
```

### Business Meaning Injection
We allow `enrich_schema(descriptions={...})` to map vague terms like "High Value Customer" to specific SQL logic (`LTV > 10000`), bridging the gap between Business and Data.
