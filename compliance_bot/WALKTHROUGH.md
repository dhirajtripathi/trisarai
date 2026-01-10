# Compliance & Audit Bot - Walkthrough

## Overview
This project is a Multi-Jurisdictional Compliance & Audit Bot. It uses a LangGraph workflow to scan draft communications against a set of regulations (EU AI Act, Insurance Laws, etc.) using an LLM. If violations are found, a "Guardrail" layer rewrites the content.

The system supports multiple LLM providers (Azure OpenAI, AWS Bedrock, Google Gemini) and allows dynamic updates to its knowledge base.

## Project Structure
- **`app.py`**: Legacy Streamlit UI.
- **`api.py`**: FastAPI Backend exposing logic for React UI.
- **`graph_workflow.py`**: Core logic (LangGraph state machine).
- **`rag_knowledge.py`**: RAG implementation (FAISS + SentenceTransformers).
- **`config.py`**: Configuration classes.
- **`ui/`**: React + Vite Frontend application.

## Prerequisites
- Python 3.9+
- Node.js & npm (for React UI)
- API Keys for your chosen LLM provider (Azure, AWS, or Google)

## Setup & Running

### 1. Backend Setup
1.  **Environment Variables**:
    Copy `.env.example` to `.env` and fill in your keys.
    ```bash
    cp .env.example .env
    ```

2.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Backend API**:
    This starts the FastAPI server on port 8000.
    ```bash
    python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
    ```
    - Swagger Documentation: http://localhost:8000/docs

### 2. Frontend Setup (React)
1.  **Install Node Dependencies**:
    Navigate to the `ui` directory.
    ```bash
    cd ui
    npm install
    ```

2.  **Run Development Server**:
    ```bash
    npm run dev
    ```
    - Access the UI at http://localhost:5173

### 3. Streamlit UI (Alternative)
If you prefer the Python-only UI:
```bash
streamlit run app.py
```

## Features & Usage

### Compliance Scanning
1.  Open the UI (React or Streamlit).
2.  Select your **LLM Provider** in the sidebar.
3.  Enter the necessary **Credentials** (API Key, Endpoint, Deployment/Model Name, etc.).
4.  Enter a **Draft Response** (e.g., a claim denial).
5.  Click **Scan**.
6.  View the **Compliance Status**, **Feedback**, and **rewritten text** (if violated).

### Knowledge Base Management
1.  In the Sidebar, go to **Knowledge Base**.
2.  Enter a defined **Source Name** (e.g., "New Company Policy").
3.  Paste the **Regulation Text**.
4.  Click **Add**.
5.  The system will now use this new rule in future scans.

## Configuration Parameters
- **Azure OpenAI**: Requires API Key, Endpoint, Deployment Name, API Version.
- **AWS Bedrock**: Requires Access Key, Secret Key, Region, Model ID.
- **Google Gemini**: Requires API Key, Model Name.

## Troubleshooting
- **`npm` not found**: Ensure Node.js is installed and added to your PATH.
- **API Errors**: Check the terminal running `uvicorn` for tracebacks. Ensure API keys are correct.
- **Embeddings**: The first run downloads the `all-MiniLM-L6-v2` model locally; this might take a minute.
