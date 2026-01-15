# Agentic Claims Adjuster (FNOL)
**Usecase Name**: `claims_adjuster`

## 1. Functional Overview
The **Autonomous Claims Adjuster** automates the First Notice of Loss (FNOL) process for Auto Insurance. It demonstrates how "Human-in-the-Loop" agents can handle multimodal input (Voice + Images) to settle simple claims in seconds ("Zero Touch Settlement").

### Key Features
*   **Multimodal Intake**: Simulates processing of accident photos (Computer Vision) and driver voice notes (Speech-to-Text).
*   **Zero-Touch Settlement**: Automatically approves straight-through claims if policy criteria are met.
*   **Cyclic Feedback**: If an image is blurry, the agent *rejects* the state and asks the user for a new photo (LangGraph Cycle).
*   **Dynamic Estimation**: Calculates payout using real-time parts & labor pricing tools.

## 2. Technical Architecture (LangGraph)
The system is implemented as a **Stateful Graph** using `LangGraph`.

### The Graph Workflow (`graph.py`)
1.  **Intake Node**:
    *   Input: Image Quality (Clear/Blurry) + Transcript.
    *   Action: Validates evidence. If invalid -> Routes back to User (`needs_input` state).
2.  **Verification Node (RAG)**:
    *   Input: Validated Damage Type.
    *   Action: Queries the "Policy Knowledge Base" (RAG) to check if "Windshield Crack" is covered.
    *   LLM Decision: "We Pay" vs "Denied".
3.  **Estimation Node (MCP Tools)**:
    *   Input: Approved Claim.
    *   Action: Calls `get_part_price` and `get_labor_rate` tools.
    *   Output: Final Settlement Amount.

### Tech Stack
*   **Orchestration**: LangGraph (State Machine).
*   **LLMs**: Azure OpenAI (GPT-4), AWS Bedrock (Claude v2), Google Gemini.
*   **Frontend**: Streamlit.

## 3. Implementation Steps

### Prerequisites
*   Python 3.10+
*   Streamlit

### Setup & Run
1.  **Navigate**: `cd claims_adjuster`
2.  **Install**: `pip install -r requirements.txt`
3.  **Run**: `streamlit run main.py`

### Testing the Agent
1.  Select **LLM Provider** in the sidebar.
2.  **Scenario A (Happy Path)**:
    *   Photo: Clear
    *   Transcript: "Rock hit my windshield."
    *   *Result*: Agent approves and estimates cost.
3.  **Scenario B (Human Loop)**:
    *   Photo: Blurry
    *   *Result*: Agent halts and requests new photo.

## 4. Agentic Concepts
*   **State Management**: The `AdjusterState` TypedDict maintains the full context (User Input -> Verdict -> Code) across node transitions.
*   **Conditional Edges**: Logic like `route_after_intake` determines the next step dynamically based on agent output.
