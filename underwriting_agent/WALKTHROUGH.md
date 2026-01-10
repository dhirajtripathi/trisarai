# Dynamic Life & Health Underwriting Agent - Walkthrough

## Overview
This application prices risk in real-time with a **Human-in-the-Loop (HITL)** architecture.

## Components
- **`main.py`**: Streamlit Dashboard.
- **`api.py`**: FastAPI Backend (serves React App, handles persistence).
- **`ui/`**: React + Vite Frontend (Polling Dashboard).
- **`graph.py`**: LangGraph with `SqliteSaver` checkpointer.

## How to Run

### Option 1: Streamlit UI
```bash
/Users/dhirajtripathi/Documents/aidev/.venv/bin/python3 -m streamlit run underwriting_agent/main.py
```
- Access at http://localhost:8507

### Option 2: React UI
**1. Start the Backend API:**
```bash
cd underwriting_agent
/Users/dhirajtripathi/Documents/aidev/.venv/bin/python3 -m uvicorn api:app --host 0.0.0.0 --port 8003
```
- API Documents available at http://localhost:8003/docs

**2. Start the Frontend:**
> [!NOTE]
> You must have `npm` installed. I have created the source code, but you need to run the following:
```bash
cd underwriting_agent/ui
npm install
npm run dev
```
- Access at http://localhost:5173

## Features
- **Persistence**: Both UIs share the same `state.db`. A case started in React can theoretically be resumed in Streamlit if the thread ID matches.
- **HITL Polling**: The React UI polls the backend every 2 seconds to check if the agent has paused for review.

## Scenarios to Test
1.  **Start Case**: Select User/Provider -> click Start.
2.  **Verify Pause**: Dashboard shows data and "Action Required".
3.  **Approval**: Click "Approve". UI updates to "Case Active".
