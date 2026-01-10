# Implementation Plan - Hyper-Personalized Policy Lifecycle Manager

## Goal Description
Build an agentic system that proactively monitors customer "Life Events" (simulated via FinTech integrations) and generates tailored insurance endorsements. The system will calculate premium changes and explain the reasoning to the customer.

## User Review Required
> [!IMPORTANT]
> **LLM Credentials**: Credentials for Azure OpenAI, AWS Bedrock, or Google Gemini can be configured directly in the React UI or passed via environment variables.

## Proposed Changes

### Project Structure
Root: `/Users/dhirajtripathi/Documents/aidev/lifecycle_manager`

#### [NEW] [config.py](file:///Users/dhirajtripathi/Documents/aidev/lifecycle_manager/config.py)
- Configuration for default Azure OpenAI Connection.
- Mock database connections.

#### [NEW] [data_models.py](file:///Users/dhirajtripathi/Documents/aidev/lifecycle_manager/data_models.py)
- Pydantic models:
    - `Customer`: Profile, current policy, risk factors.
    - `LifeEvent`: Type, details, timestamp.
    - `EndorsementProposal`: Proposed changes, premium delta, reasoning.

#### [NEW] [pricing_engine.py](file:///Users/dhirajtripathi/Documents/aidev/lifecycle_manager/pricing_engine.py)
- Deterministic logic to calculate premium changes based on risk modifiers (e.g., +15% for new car, +20% for marriage/new home bundle discount logic).

#### [NEW] [agent.py](file:///Users/dhirajtripathi/Documents/aidev/lifecycle_manager/agent.py)
- **LangGraph Workflow**:
    - **Node 1: Event Analyzer**: Determines what coverage changes are needed based on the life event.
    - **Node 2: Pricing Calculator**: Calls `pricing_engine` to get exact numbers.
    - **Node 3: Communication Drafter**: Uses LLM (Dynamically instantiated based on provider selection) to draft a personalized email/message explaining the "Why" and the "How much".
    - **Edge**: Event -> Analyzer -> Pricing -> Drafter -> End.

#### [NEW] [api.py](file:///Users/dhirajtripathi/Documents/aidev/lifecycle_manager/api.py)
- FastAPI application.
- Endpoints:
    - `POST /simulate-event`: Accepts event details, provider config, credential overrides. Runs agent, returns proposal and draft.
    - `GET /customer`: Returns current customer profile.

#### [NEW] [ui/](file:///Users/dhirajtripathi/Documents/aidev/lifecycle_manager/ui/)
- React + Vite application.
- **Components**:
    - `Dashboard`: Main view.
    - `EventSimulator`: Buttons to trigger events.
    - `AgentFeed`: Displays the "thinking" process and final output.
    - `CredentialsConfig`: Input fields for specific LLM providers.

## Verification Plan
### Manual Verification
1.  **Run API**: Start `uvicorn` on port 8000.
2.  **Run React App**: Start dev server on port 5173.
3.  **Simulate Event**: Click "Marriage" in React UI.
4.  **Observation**: API returns specific pricing; UI updates to show proposal.
