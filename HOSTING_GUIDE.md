# Nexus OS: Implementation & Hosting Guide

## 1. Project Overview
This repository contains a suite of **12 Autonomous AI Agents** designed for the Enterprise (FSI, Data, DevOps). They are orchestrated via a **Unified Portal**.

## 2. Quick Start (GitHub Codespaces)
The project is optimized for Codespaces.

1.  **Open Codespace**: Launch a new Codespace on `main` branch.
2.  **Wait for Install**: The `.devcontainer` automatically runs `setup.sh` to install generic dependencies (Python, Node).
3.  **Launch Suite**:
    ```bash
    ./start_all.sh
    ```
4.  **Access Portal**:
    *   Open the **Ports** tab in VS Code.
    *   Click the Globe icon next to **Port 3000** (`unified_portal`).
    *   *Note: Ensure all other ports (5173-8506) are also "Public" or "Forwarded".*

## 3. Port Mapping Table

| Domain | Agent Name | UI Port | Technology |
| :--- | :--- | :--- | :--- |
| **Portal** | **Unified Enterprise Portal** | **3000** | React/Vite |
| **Data** | Text-to-SQL Platform | 5173 | React/Vite |
| **Data** | RAG Knowledge Base | 5174 | React/Vite |
| **FSI** | Agentic KYC Platform | 5175 | React/Vite |
| **Dev** | API Transformation Agent | 5176 | React/Vite |
| **Dev** | Integration Migration Agent | 5177 | React/Vite |
| **Dev** | AI DDO (Delivery Orchestrator)| 5178 | React/Vite |
| **FSI** | Computer Vision FNOL | 8501 | Streamlit |
| **FSI** | Fraud Investigator | 8502 | Streamlit |
| **FSI** | Dynamic Underwriting | 8503 | Streamlit |
| **FSI** | Compliance Bot | 8504 | Streamlit |
| **Dev** | Lifecycle Manager | 8506 | Streamlit |

## 4. Configuration
### API Keys
Create a `config.json` in the root (optional) or set Environment Variables in Codespaces secrets.
*   `AZURE_OPENAI_API_KEY`
*   `AZURE_OPENAI_ENDPOINT`
*   `JIRA_API_TOKEN` (for AI DDO)

### Persistence
*   **Databases**: Agents use SQLite (`agents.db`, `claims.db`) which persists in the workspace.
*   **Uploads**: `uploads/` directories are local.

## 5. Troubleshooting
*   **"Port 517x already in use"**:
    *   Kill zombie processes: `pkill -f "vite"` or `pkill -f "streamlit"`.
    *   Restart: `./start_all.sh`.
*   **"Connection Refused" in Portal**:
    *   Check the VS Code "Ports" tab. If a port is missing, click "Add Port" and type the number manually.
