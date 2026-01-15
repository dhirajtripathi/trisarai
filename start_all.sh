#!/bin/bash
source .venv/bin/activate

# Cleanup on exit
trap 'kill $(jobs -p)' EXIT

echo "🚀 Launching Nexus Agentic Suite..."

# --- 1. APIs & Streamlit Backends (Ports 8000-85xx) ---
echo "Starting Backend Services..."

# Data Intelligence
python3 -m uvicorn text_to_sql_mcp.main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
python3 -m uvicorn rag_mcp_server.main:app --host 0.0.0.0 --port 8001 > /dev/null 2>&1 &

# FSI Agents (Streamlit Apps typically run on 8501, we need to specific ports)
streamlit run claims_adjuster/main.py --server.port 8501 --server.headings.transparent=true > /dev/null 2>&1 &
streamlit run fraud_investigator/app.py --server.port 8502 --server.headings.transparent=true > /dev/null 2>&1 &
streamlit run underwriting_agent/main.py --server.port 8503 --server.headings.transparent=true > /dev/null 2>&1 &
streamlit run compliance_bot/app.py --server.port 8504 --server.headings.transparent=true > /dev/null 2>&1 &

# Developer Tools (Streamlit & APIs)
streamlit run api_transformation_agent/ui/Home.py --server.port 8505 --server.headings.transparent=true > /dev/null 2>&1 &
python3 -m uvicorn integration_migration_agent.api:app --host 0.0.0.0 --port 8005 > /dev/null 2>&1 &
python3 -m uvicorn ai_ddo.api:app --host 0.0.0.0 --port 8006 > /dev/null 2>&1 &
streamlit run lifecycle_manager/main.py --server.port 8506 --server.headings.transparent=true > /dev/null 2>&1 &

# --- 2. Frontend UIs (Ports 3000, 5173+) ---
echo "Starting Frontends..."

# Master Portal (Port 3000)
cd unified_portal && npm run dev -- --host --port 3000 > /dev/null 2>&1 &

# Agent UIs
# Note: Some agents use Streamlit (above), others have React UIs.
cd text_to_sql_ui && npm run dev -- --host --port 5173 > /dev/null 2>&1 &
# rag_mcp_ui -> 5174
# kyc_dashboard_ui -> 5175
if [ -d "rag_mcp_ui" ]; then cd rag_mcp_ui && npm run dev -- --host --port 5174 > /dev/null 2>&1 &; fi
if [ -d "kyc_dashboard_ui" ]; then cd kyc_dashboard_ui && npm run dev -- --host --port 5175 > /dev/null 2>&1 &; fi

# Wait for startup
sleep 5

echo "--------------------------------------------------------"
echo "✅ NEXUS OS DEPLOYED | Access Points:"
echo "--------------------------------------------------------"
echo "🖥️  UNIFIED PORTAL    : http://localhost:3000"
echo "--------------------------------------------------------"
echo "📊 Text-to-SQL       : http://localhost:5173"
echo "📚 RAG Knowledge     : http://localhost:5174"
echo "🆔 KYC Dashboard     : http://localhost:5175"
echo "🚗 Claims Adjuster   : http://localhost:8501"
echo "🕵️  Fraud SIU         : http://localhost:8502"
echo "📝 Underwriting      : http://localhost:8503"
echo "⚖️  Compliance Bot    : http://localhost:8504"
echo "🔁 API Transformer   : http://localhost:8505"
echo "🔄 Lifecycle Mgr     : http://localhost:8506"
echo "--------------------------------------------------------"
echo "Press Ctrl+C to stop all agents."

wait
