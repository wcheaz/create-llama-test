#!/bin/bash

# Comprehensive script to manage LlamaIndex application

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if a port is in use
is_port_in_use() {
    local port=$1
    lsof -i:$port >/dev/null 2>&1
}

# Function to check if a process is running and kill it
stop_process() {
    local process_name="$1"
    local port="$2"
    
    print_status $BLUE "Checking for $process_name processes on port $port..."
    
    # Find and kill processes using the specified port
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        print_status $YELLOW "Stopping $process_name (PID: $pid) on port $port..."
        kill -TERM $pid 2>/dev/null || true
        sleep 3
        
        # Force kill if still running
        if is_port_in_use $port; then
            print_status $RED "Force killing $process_name..."
            kill -9 $pid 2>/dev/null || true
            sleep 2
        fi
        
        print_status $GREEN "$process_name stopped"
    else
        print_status $GREEN "No $process_name process found on port $port"
    fi
}

# Function to stop workflow deployment
stop_workflow() {
    print_status $BLUE "Checking for workflow deployments..."
    
    # Try to get list of deployments
    local deployments=$(uv run llamactl list 2>/dev/null || echo "")
    
    if [[ $deployments == *"chat"* ]]; then
        print_status $YELLOW "Stopping existing 'chat' deployment..."
        uv run llamactl delete chat 2>/dev/null || true
        print_status $GREEN "Workflow deployment stopped"
    else
        print_status $GREEN "No 'chat' deployment found"
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_status $BLUE "Checking prerequisites..."
    
    # Check if uv is installed
    if ! command -v uv &> /dev/null; then
        print_status $RED "Error: uv is not installed. Please install it first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_status $RED "Error: .env file not found. Please create it with your API keys."
        exit 1
    fi
    
    # Check if data directory exists and has files
    if [ ! -d "data" ] || [ -z "$(ls -A data 2>/dev/null)" ]; then
        print_status $RED "Error: data directory is empty or doesn't exist."
        exit 1
    fi
    
    print_status $GREEN "Prerequisites check passed"
}

# Function to show application status
show_status() {
    print_status $BLUE "=== Application Status ==="
    
    # Check API server
    if is_port_in_use 4501; then
        local api_pid=$(lsof -ti:4501)
        print_status $GREEN "API Server: RUNNING (PID: $api_pid, Port: 4501)"
    else
        print_status $RED "API Server: STOPPED"
    fi
    
    # Check control plane
    if is_port_in_use 8000; then
        local control_pid=$(lsof -ti:8000)
        print_status $GREEN "Control Plane: RUNNING (PID: $control_pid, Port: 8000)"
    else
        print_status $RED "Control Plane: STOPPED"
    fi
    
    # Check UI
    if is_port_in_use 3000; then
        local ui_pid=$(lsof -ti:3000)
        print_status $GREEN "UI Server: RUNNING (PID: $ui_pid, Port: 3000)"
    else
        print_status $RED "UI Server: STOPPED"
    fi
    
    # Check workflow deployment
    local deployments=$(uv run llamactl list 2>/dev/null || echo "")
    if [[ $deployments == *"chat"* ]]; then
        print_status $GREEN "Workflow Deployment: RUNNING (name: chat)"
    else
        print_status $RED "Workflow Deployment: STOPPED"
    fi
}

# Function to start the application
start_app() {
    print_status $BLUE "=== Starting LlamaIndex Application ==="
    
    # Check prerequisites
    check_prerequisites
    
    # Generate embeddings if needed
    print_status $BLUE "Checking if embeddings need to be generated..."
    if [ ! -d "./output" ] || [ -z "$(ls -A ./output 2>/dev/null)" ]; then
        print_status $YELLOW "Generating embeddings..."
        uv run generate
        print_status $GREEN "Embeddings generated successfully"
    else
        print_status $GREEN "Embeddings already exist, skipping generation"
    fi
    
    # Start API server in background
    print_status $YELLOW "Starting API server..."
    uv run -m llama_deploy.apiserver > server.log 2>&1 &
    API_PID=$!
    print_status $GREEN "API server started with PID: $API_PID"
    
    # Wait for API server to start
    print_status $BLUE "Waiting for API server to initialize..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if is_port_in_use 4501; then
            print_status $GREEN "API server is ready!"
            break
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        print_status $RED "API server failed to start within expected time. Check server.log for details."
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
    
    # Deploy the workflow
    print_status $YELLOW "Deploying workflow..."
    if uv run llamactl deploy llama_deploy.yml; then
        print_status $GREEN "Workflow deployed successfully!"
    else
        print_status $RED "Failed to deploy workflow. Check server.log for details."
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
    
    # Show final status
    print_status $GREEN "\n=== Application started successfully! ==="
    print_status $BLUE "API Server: http://localhost:4501"
    print_status $BLUE "UI Interface: http://localhost:4501/deployments/chat/ui"
    print_status $BLUE "API Documentation: http://localhost:4501/docs"
    print_status $YELLOW "\nTo stop the application, run: ./manage_app.sh stop"
    print_status $YELLOW "Or press Ctrl+C in this terminal to stop the API server"
}

# Function to stop the application
stop_app() {
    print_status $BLUE "=== Stopping LlamaIndex Application ==="
    
    stop_process "API server" 4501
    stop_process "Control plane" 8000
    stop_process "UI server" 3000
    stop_workflow
    
    print_status $GREEN "\n=== Application stopped successfully ==="
}

# Function to restart the application
restart_app() {
    print_status $BLUE "=== Restarting LlamaIndex Application ==="
    stop_app
    sleep 2
    start_app
}

# Main script logic
case "${1:-}" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        show_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the application (stops any existing instances first)"
        echo "  stop    - Stop the application"
        echo "  restart - Restart the application"
        echo "  status  - Show the current status of all components"
        exit 1
        ;;
esac