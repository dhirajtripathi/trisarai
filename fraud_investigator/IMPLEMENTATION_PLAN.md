# Implementation Plan - Real-Time Fraud "Private Investigator"

## Goal Description
Build a "Counter-Intelligence" agent that detects insurance fraud in real-time. It uses an agentic workflow to cross-reference data, detect visual anomalies in claim photos, and flag high-risk claims for human review.

## User Review Required
> [!IMPORTANT]
> **MCP & Guardrails**: This project emphasizes "Model Context Protocol" (simulated via strict tool interfaces) and "Guardrails" (output validation) to ensure safety and reliability.

## Proposed Changes

### Project Structure
Root: `/Users/dhirajtripathi/Documents/aidev/fraud_investigator`

#### [NEW] [config.py](file:///Users/dhirajtripathi/Documents/aidev/fraud_investigator/config.py)
- Azure OpenAI settings.
- Threshold configurations (e.g., `ReviewThreshold = 75`).

#### [NEW] [utils/data_sources.py](file:///Users/dhirajtripathi/Documents/aidev/fraud_investigator/utils/data_sources.py)
- **MCP-style Tools**:
    - `check_social_media(name, date)`: Simulation of checking public posts.
    - `check_ghost_broking_db(policy_id)`: Checks known fraud patterns.
    - `analyze_claim_photo(photo_hash)`: Checks if photo exists in "Recycled Photos" DB.

#### [NEW] [utils/guardrails.py](file:///Users/dhirajtripathi/Documents/aidev/fraud_investigator/utils/guardrails.py)
- Validators to ensure the agent's explanation is objective and unbiased.
- Filters out "hallucinated" evidence not found in the tools.

#### [NEW] [graph.py](file:///Users/dhirajtripathi/Documents/aidev/fraud_investigator/graph.py)
- **LangGraph Workflow**:
    - **State**: `claim_details`, `evidence_log`, `fraud_score`, `human_review_needed`.
    - **Nodes**:
        1.  `Investigation`: Calls tools to gather data.
        2.  `RiskAssessment`: LLM synthesizes data into a score.
            - *Guardrail Check*: Validates the reasoning.
        3.  `HumanReview`: (HitL) Pauses if score > threshold.
    - **Edges**: Conditional logic based on score.

#### [MODIFY] [graph.py](file:///Users/dhirajtripathi/Documents/aidev/fraud_investigator/graph.py)
- Update `AgentState` to include `provider` and `credentials`.
- Update `get_llm` to instantiate `AzureChatOpenAI`, `ChatBedrock`, or `ChatGoogleGenerativeAI` based on the selected provider.

#### [NEW] [api.py](file:///Users/dhirajtripathi/Documents/aidev/fraud_investigator/api.py)
- FastAPI application to expose the agent.
- Endpoints:
    - `GET /claims`: Returns simulated claims.
    - `POST /investigate`: Accepts claim details + provider config, runs `app_graph`, returns evidence and score.

#### [NEW] [ui/](file:///Users/dhirajtripathi/Documents/aidev/fraud_investigator/ui/)
- React + Vite application.
- **Components**:
    - `InvestigationConsole`: Main dashboard.
    - `ClaimFeed`: Sidebar list of claims.
    - `EvidenceBoard`: Visual display of gathered intel.
    - `ProviderConfig`: UI for LLM selection and credentials.

#### [MODIFY] [app.py](file:///Users/dhirajtripathi/Documents/aidev/fraud_investigator/app.py)
- **Settings Sidebar**: Add dropdown for "LLM Provider".
- **Dynamic Inputs**: Show relevant API Key/Region/Endpoint fields based on selection.
- **Pass Credentials**: Inject selected details into the `app_graph` state.

## Verification Plan
### Manual Verification
1.  **Azure**: Test existing flow (John Doe Fake).
2.  **AWS**: Configure Bedrock creds -> Test.
3.  **Gemini**: Configure Google Key -> Test.
