#!/bin/bash
echo "🚀 Setting up Nexus OS Environment..."

# 1. Setup Python
echo "🐍 Setting up Python Virtual Environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip

# Install Core & Shared Libs
pip install fastapi uvicorn sqlalchemy litellm langchain langgraph streamlit pandas numpy requests pytest chromadb sentence-transformers

# Install Specific Requirements (Iterate widely)
echo "📦 Installing Agent Dependencies..."
find . -name "requirements.txt" -not -path "./.venv/*" -not -path "./node_modules/*" | while read req_file; do
    echo "   -> Installing from $req_file"
    pip install -r "$req_file"
done

# 2. Setup Node
echo "⚛️ Installing Node Dependencies..."

# Function to npm install if package.json exists
install_node() {
    if [ -d "$1" ] && [ -f "$1/package.json" ]; then
        echo "   -> $1"
        cd "$1" && npm install > /dev/null 2>&1 && cd - > /dev/null
    fi
}

install_node "unified_portal"
install_node "text_to_sql_ui"
install_node "rag_mcp_ui"
install_node "kyc_dashboard_ui"
install_node "agentic_kyc_platform/ui"
install_node "underwriting_agent/ui"
install_node "integration_migration_agent/ui"
install_node "ai_ddo/ui"
install_node "lifecycle_manager/ui"
install_node "claims_adjuster/ui"
install_node "fraud_investigator/ui"

echo "✅ Setup Complete! Run './start_all.sh' to launch Nexus_OS."
