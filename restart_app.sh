#!/bin/bash

# Script to stop existing LlamaIndex workflow and API server, then restart them

echo "=== LlamaIndex Application Restart Script ==="

# Function to check if a process is running and kill it
stop_process() {
    local process_name="$1"
    local port="$2"
    
    echo "Checking for existing $process_name processes on port $port..."
    
    # Find and kill processes using the specified port
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        echo "Stopping $process_name (PID: $pid) on port $port..."
        kill -9 $pid 2>/dev/null
        sleep 2
        echo "$process_name stopped"
    else
        echo "No $process_name process found on port $port"
    fi
}

# Function to stop workflow deployment
stop_workflow() {
    echo "Checking for existing workflow deployments..."
    
    # Try to get list of deployments
    local deployments=$(uv run llamactl list 2>/dev/null)
    
    if [[ $deployments == *"chat"* ]]; then
        echo "Stopping existing 'chat' deployment..."
        uv run llamactl delete chat 2>/dev/null
        echo "Workflow deployment stopped"
    else
        echo "No 'chat' deployment found"
    fi
}

# Step 1: Stop existing processes
echo -e "\n=== Step 1: Stopping existing processes ==="

# Stop API server (port 4501)
stop_process "API server" 4501

# Stop control plane (port 8000)
stop_process "Control plane" 8000

# Stop UI (port 3000)
stop_process "UI server" 3000

# Stop workflow deployment
stop_workflow

# Step 2: Start the application
echo -e "\n=== Step 2: Starting the application ==="

# Generate embeddings if needed
echo "Checking if embeddings need to be generated..."
if [ ! -d "./output" ] || [ -z "$(ls -A ./output 2>/dev/null)" ]; then
    echo "Generating embeddings..."
    uv run generate
else
    echo "Embeddings already exist, skipping generation"
fi

# Start API server in background
echo "Starting API server..."
uv run -m llama_deploy.apiserver > server.log 2>&1 &
API_PID=$!
echo "API server started with PID: $API_PID"

# Wait for API server to start
echo "Waiting for API server to initialize..."
sleep 5

# Deploy the workflow
echo "Deploying workflow..."
uv run llamactl deploy llama_deploy.yml

# Check if deployment was successful
if [ $? -eq 0 ]; then
    echo -e "\n=== Application started successfully! ==="
    echo "API Server: http://localhost:4501"
    echo "UI Interface: http://localhost:4501/deployments/chat/ui"
    echo "API Documentation: http://localhost:4501/docs"
    echo ""
    echo "To stop the application, run: ./stop_app.sh"
    echo "Or press Ctrl+C in this terminal to stop the API server"
else
    echo "Failed to deploy workflow. Check server.log for details."
    kill $API_PID 2>/dev/null
    exit 1
fi