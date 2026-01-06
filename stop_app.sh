#!/bin/bash

# Script to stop LlamaIndex workflow and API server

echo "=== Stopping LlamaIndex Application ==="

# Function to check if a process is running and kill it
stop_process() {
    local process_name="$1"
    local port="$2"
    
    echo "Checking for $process_name processes on port $port..."
    
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
    echo "Checking for workflow deployments..."
    
    # Try to get list of deployments
    local deployments=$(uv run llamactl list 2>/dev/null)
    
    if [[ $deployments == *"chat"* ]]; then
        echo "Stopping 'chat' deployment..."
        uv run llamactl delete chat 2>/dev/null
        echo "Workflow deployment stopped"
    else
        echo "No 'chat' deployment found"
    fi
}

# Stop all components
stop_process "API server" 4501
stop_process "Control plane" 8000
stop_process "UI server" 3000
stop_workflow

echo -e "\n=== Application stopped successfully ==="