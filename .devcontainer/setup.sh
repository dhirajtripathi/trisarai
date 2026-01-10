#!/bin/bash
echo "🚀 Setting up Nexus OS Environment..."

# 1. Setup Python
echo "🐍 Setting up Python Virtual Environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# Install requirements for all agents
echo "📦 Installing Python Dependencies..."
pip install -r underwriting_agent/requirements.txt
pip install -r integration_migration_agent/requirements.txt
# Add others if they exist or consolidate
pip install fastapi uvicorn langchain langgraph pandas numpy requests pytest

# 2. Setup Node
echo "⚛️ Installing Node Dependencies..."

echo " -> Unified Portal"
cd unified_portal && npm install && cd ..

echo " -> Underwriting UI"
cd underwriting_agent/ui && npm install && cd ../..

echo " -> Integration Migration UI"
cd integration_migration_agent/ui && npm install && cd ../..

# Add others similarly...
# For this PoC heavily used folders:
if [ -d "claims_adjuster/ui" ]; then
    echo " -> Claims UI"
    cd claims_adjuster/ui && npm install && cd ../..
fi
if [ -d "fraud_investigator/ui" ]; then
    echo " -> Fraud UI"
    cd fraud_investigator/ui && npm install && cd ../..
fi
if [ -d "lifecycle_manager/ui" ]; then
    echo " -> Lifecycle UI"
    cd lifecycle_manager/ui && npm install && cd ../..
fi

echo "✅ Setup Complete! Run './start_all.sh' to launch."
