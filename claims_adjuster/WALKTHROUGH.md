# Autonomous "Straight-Through" Claims Adjuster - Walkthrough

## Overview
This application automates the First Notice of Loss (FNOL) process using a **Multi-Agent Cyclic Workflow**.

## Components
- **`main.py`**: Streamlit Chat Interface.
- **`api.py`**: FastAPI Backend (serves the React App).
- **`ui/`**: React + Vite Frontend.
- **`graph.py`**: LangGraph Workflow (Multi-Provider).

## How to Run

### Option 1: Streamlit UI
```bash
/Users/dhirajtripathi/Documents/aidev/.venv/bin/python3 -m streamlit run claims_adjuster/main.py
```
- Access at http://localhost:8505

### Option 2: React UI
**1. Start the Backend API:**
```bash
cd claims_adjuster
/Users/dhirajtripathi/Documents/aidev/.venv/bin/python3 -m uvicorn api:app --host 0.0.0.0 --port 8002
```
- API Documents available at http://localhost:8002/docs

**2. Start the Frontend:**
> [!NOTE]
> You must have `npm` installed. I have created the source code, but you need to run the following:
```bash
cd claims_adjuster/ui
npm install
npm run dev
```
- Access at http://localhost:5173

## Configuration
- **Provider Selection**: Both UIs allow you to select **Azure OpenAI**, **AWS Bedrock**, or **Google Gemini**.
- **Credentials**: Enter keys in the settings sidebar/panel.

## Scenarios to Test
1.  **Blurry Photo**: Submit "Blurry" -> See "Action Required".
2.  **Success**: Submit "Clear" + "Windshield" -> See "Settled".
3.  **Denial**: Submit "Clear" + "Off-road" -> See "Denied".
