# Agentic Lifecycle Manager
**Usecase Name**: `lifecycle_manager`

## 1. Functional Overview
The **Lifecycle Manager** is a proactive agent that manages the end-to-end lifecycle of an Insurance Customer. Instead of waiting for a claim, it monitors "Life Events" (Marriage, New Home, Child) to recommend policy updates, ensuring coverage gap protection.

### Key Features
*   **Event Simulation**: Simulates the passage of time and random life events for demo purposes.
*   **Gap Analysis**: Events (e.g., "Bought a Boat") vs Current Policy -> "Gap Detected".
*   **Pricing Engine**: Autonomously calculates the premium difference for the endorsement.
*   **Nudge Generation**: Writes a personalized email contextually explaining the need for the update.

## 2. Technical Architecture
An Event-Driven Agent loop.

### Core Components
1.  **State Machine (`main.py`)**:
    *   Tracks "Customer State" (Age, Assets, Marital Status).
2.  **Pricing Engine (`pricing_engine.py`)**:
    *   Python-based rate calculator (Deterministic logic).
3.  **Agent Core (`agent.py`)**:
    *   LLM that interprets the semantic meaning of events.
    *   "Is 'Adopting a rescue dog' a risk event?" -> Yes, Liability coverage check.

## 3. Implementation Steps

### Prerequisites
*   Python 3.10+
*   Streamlit

### Setup & Run
1.  **Navigate**: `cd lifecycle_manager`
2.  **Install**: `pip install -r requirements.txt`
3.  **Run**: `streamlit run main.py`

## 4. Context Engineering
*   **Temporal Context**: The agent maintains a timeline view, understanding that a "New Baby" event today changes the financial needs for the *next 18 years* (e.g., Term Life).
*   **Tone Matching**: The "Nudge" email adapts tone based on the event (Celebratory for Marriage, Empathetic for Loss).
