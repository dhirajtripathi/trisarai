# Dynamic Underwriting Agent
**Usecase Name**: `underwriting_agent`

## 1. Functional Overview
The **Dynamic Underwriting Agent** brings algorithmic speed to complex Risk Assessment. It moves beyond static actuarial tables to incorporate real-time context (IoT data, News, Health Trends) into Life & Health policy pricing.

### Key Features
*   **Contextual Risk Scoring**: Ingests medical history + lifestyle data (simulated IoT wearables).
*   **Dynamic Pricing**: Adjusts premiums in real-time based on risk profile.
*   **Policy Generation**: Drafts the policy document automatically.
*   **Explanation**: "Why is my premium $500?" -> "Because your BMI is X and skydiving frequency is Y."

## 2. Technical Architecture (LangGraph)
A stateful workflow managing the "submission-to-quote" lifecycle.

### Workflow Nodes (`graph.py`)
1.  **Ingest Node**: Parses application forms (PDF/JSON).
2.  **Risk Analysis Node**:
    *   Consults "Medical Guidelines" (RAG).
    *   Calculates Base Rate + Risk Loadings.
3.  **Pricing Node**:
    *   Applies business rules margins.
4.  **Drafting Node**:
    *   Generates the final Quote Letter.

## 3. Implementation Steps

### Prerequisites
*   Python 3.10+
*   Streamlit

### Setup & Run
1.  **Navigate**: `cd underwriting_agent`
2.  **Install**: `pip install -r requirements.txt`
3.  **Run**: `streamlit run main.py`

## 4. Agentic Concepts
*   **Tool Use**: The agent uses a `calculator` tool to ensure math accuracy for premiums (LLMs are bad at math!).
*   **Human-in-the-Loop**: If the Calculated Risk Score > 90 (High Risk), the graph pauses and routes to a "Manual Underwriter" queue.
