#!/bin/bash
source .venv/bin/activate

# Function to kill all background jobs on exit
trap 'kill $(jobs -p)' EXIT

echo "🚀 Launching Nexus OS..."

# Backends
echo "Starting Backends..."
python3 -m uvicorn underwriting_agent.api:app --host 0.0.0.0 --port 8003 &
python3 -m uvicorn integration_migration_agent.api:app --host 0.0.0.0 --port 8005 &
# Add others...

# Frontends
echo "Starting Frontends..."
cd unified_portal && npm run dev -- --host &
cd ../underwriting_agent/ui && npm run dev -- --host &
cd ../../integration_migration_agent/ui && npm run dev -- --host &

# Wait to ensure they start
sleep 5

echo "---------------------------------------------------"
echo "🌐 Nexus OS is LIVE"
echo "   Unified Portal: http://localhost:3000"
echo "   Migration Agent: http://localhost:5178 (API: 8005)"
echo "   Underwriter: http://localhost:5173 (API: 8003)"
echo "---------------------------------------------------"
echo "Press Ctrl+C to stop all services."

wait
