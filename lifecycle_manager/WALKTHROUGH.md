# Hyper-Personalized Policy Lifecycle Manager - Walkthrough

## Overview
This application turns insurance into a proactive service. It monitors customer "Life Events" (simulated) and uses an **Agentic Workflow** to:
1.  **Analyze** the event's impact on risk.
2.  **Calculate** precise premium changes (Pricing Engine).
3.  **Draft** personalized communication explaining the "Why" and "How much".

## Components
- **`main.py`**: Streamlit Dashboard.
- **`api.py`**: FastAPI Backend (for React UI).
- **`ui/`**: React + Vite Customer Portal.
- **`agent.py`**: LangGraph Agent (Analysis -> Pricing -> Drafting).
- **`pricing_engine.py`**: Deterministic logic for premiums.

## How to Run

### 1. Backend & Streamlit
**Run Streamlit UI:**
```bash
/Users/dhirajtripathi/Documents/aidev/.venv/bin/python3 -m streamlit run lifecycle_manager/main.py
```
- Access at http://localhost:8502

**Run API (Required for React UI):**
```bash
cd lifecycle_manager
/Users/dhirajtripathi/Documents/aidev/.venv/bin/python3 -m uvicorn api:app --host 0.0.0.0 --port 8000
```
- API Docs at http://localhost:8000/docs

### 2. React UI
> [!IMPORTANT]
> Since `npm` was not found, the `ui/` folder contains the source code but you must install dependencies manually.

**Steps:**
1.  Navigate to `lifecycle_manager/ui`.
2.  Install dependencies: `npm install`.
3.  Run dev server: `npm run dev`.
4.  Access at http://localhost:5173.

## Features
- **Simulate Life Events**: "Marriage", "New Home", "New Car".
- **Real-time Pricing**: Dynamic premium calculation.
- **Agent Drafting**: Generates personalized emails explanations.
- **Multi-LLM Support**: Configure Azure, AWS, or Gemini in the UI.

## Configuration
Click **Configure LLM Provider** in the UI sidebar to set specific credentials:
- **Azure**: API Key, Endpoint, Deployment, API Version.
- **AWS**: Access Key, Secret Key, Region, Model ID.
- **Gemini**: API Key, Model Name.
