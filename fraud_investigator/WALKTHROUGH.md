# Real-Time Fraud "Private Investigator" - Walkthrough

## Overview
This application acts as a counter-intelligence unit for insurance claims, available via **Streamlit** (Python) or **React** (Web).

## Components
- **`app.py`**: Streamlit Dashboard.
- **`api.py`**: FastAPI Backend (serves the React App).
- **`ui/`**: React + Vite Frontend.
- **`graph.py`**: Agent Logic (Multi-Provider).

## How to Run

### Option 1: Streamlit UI (Quickest)
```bash
/Users/dhirajtripathi/Documents/aidev/.venv/bin/python3 -m streamlit run fraud_investigator/app.py
```
- Access at http://localhost:8504

### Option 2: React UI (Modern)
**1. Start the Backend API:**
```bash
cd fraud_investigator
/Users/dhirajtripathi/Documents/aidev/.venv/bin/python3 -m uvicorn api:app --host 0.0.0.0 --port 8001
```
- API Documents available at http://localhost:8001/docs

**2. Start the Frontend:**
> [!NOTE]
> You must have `npm` installed. I have created the source code, but you need to run the following:
```bash
cd fraud_investigator/ui
npm install
npm run dev
```
- Access at http://localhost:5173

## Configuration
- **Provider Selection**: Both UIs allow you to select **Azure OpenAI**, **AWS Bedrock**, or **Google Gemini**.
- **Credentials**: Enter keys in the settings sidebar/panel.

## Scenarios to Test
1.  **High Risk**: "John Doe Fake" -> Agent finds Ghost Broking DB match.
2.  **Recycled Photo**: "Project X Party" -> Agent finds social media contradiction.
3.  **Low Risk**: "Sarah Smith" -> Auto-Approved.
