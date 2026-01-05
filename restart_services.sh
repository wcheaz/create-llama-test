#!/bin/bash

# Script to stop and restart LlamaDeploy services
# This script will:
# 1. Stop any running API server and LlamaDeploy processes
# 2. Restart the API server
# 3. Redeploy the LlamaDeploy workflow

echo "🔄 Restarting LlamaDeploy services..."

# Function to check if a process is running and kill it
stop_process() {
    local process_name=$1
    local pids=$(pgrep -f "$process_name")
    
    if [ -n "$pids" ]; then
        echo "🛑 Stopping $process_name processes (PIDs: $pids)..."
        pkill -f "$process_name"
        sleep 2
        # Force kill if still running
        pkill -9 -f "$process_name" 2>/dev/null
    else
        echo "✅ No $process_name processes found running"
    fi
}

# Stop API server processes
stop_process "llama_deploy.apiserver"
stop_process "uvicorn.*llama_deploy"

# Stop any llamactl processes
stop_process "llamactl"

# Clean up any potential port占用
echo "🧹 Cleaning up ports 4501 and 8000..."
lsof -ti:4501 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Clean up temporary deployment directory
echo "🧹 Cleaning up temporary deployment directory..."
rm -rf /tmp/llama_deploy

# Wait a moment for processes to fully stop
sleep 3

echo ""
echo "🚀 Starting API server..."
# Start the API server in background and redirect output to apiserver.log
uv run -m llama_deploy.apiserver > apiserver.log 2>&1 &
API_SERVER_PID=$!
echo "API server started with PID: $API_SERVER_PID"
echo "API server output will be logged to apiserver.log"

# Wait for API server to start
echo "⏳ Waiting for API server to initialize..."
sleep 5

# Check if API server is running
if ! kill -0 $API_SERVER_PID 2>/dev/null; then
    echo "❌ Failed to start API server"
    exit 1
fi

echo ""
echo "📦 Deploying LlamaDeploy workflow..."
# Deploy the workflow
uv run llamactl deploy llama_deploy.yml

# Check if deployment was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Services restarted successfully!"
    echo ""
    echo "📌 Access the chat UI at: http://localhost:4501/deployments/chat/ui"
    echo "📌 API documentation at: http://localhost:4501/docs"
    echo ""
    echo "💡 To stop services later, run:"
    echo "   pkill -f 'llama_deploy.apiserver'"
    echo "   pkill -f 'uvicorn.*llama_deploy'"
else
    echo "❌ Failed to deploy workflow"
    # Clean up the API server if deployment failed
    kill $API_SERVER_PID 2>/dev/null
    exit 1
fi