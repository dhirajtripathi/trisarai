# Integration Migration Agent
**Usecase Name**: `integration_migration_agent`

## 1. Functional Overview
The **Integration Migration Agent** focuses on replatforming integration logic. It helps move from proprietary middleware (e.g., TIBCO, WebMethods, MuleSoft) to Cloud-Native microservices (Spring Boot, Azure Logic Apps).

### Key Features
*   **Logic Extraction**: Reads XML flow definitions from legacy exports.
*   **Pattern Recognition**: "This flow is a 'Scatter-Gather' pattern."
*   **Code Generation**: Writes standard Java/Spring Boot code or Logic Apps JSON to replicate the pattern.
*   **Test Generation**: Auto-generates JUnit tests based on the input/output schema.

## 2. Technical Architecture (LangGraph)
Uses a graph to manage the iterative refactoring process.

### Workflow Nodes (`graph.py`)
1.  **Assess Node**:
    *   Analyzes complexity (Lines of Code, Logic Depth).
    *   Estimates migration effort.
2.  **Plan Node**:
    *   Proposes a Target Architecture (e.g., "Split into 3 microservices").
3.  **Convert Node**:
    *   LLM-driven Syntax Translation (proprietary XML -> Java).
4.  **Verify Node**:
    *   Compiles code (Sandboxed environment).

## 3. Implementation Steps

### Prerequisites
*   Python 3.10+
*   Java JDK 17 (for validation)

### Setup & Run
1.  **Navigate**: `cd integration_migration_agent`
2.  **Install**: `pip install -r requirements.txt`
3.  **Run**: `streamlit run ui/app.py`

## 4. Context Engineering
*   **Library Injection**: The agent is prompted with the documentation of the *Target* framework (e.g., "Here is how you handle Retry logic in Spring Boot 3").
*   **One-Shot Examples**: We provide "Rosetta Stone" examples (Mule DataWeave snippet -> Java Stream equivalant) to guide the LLM.
