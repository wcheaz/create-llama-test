# LlamaIndex Workflow Example - Setup Guide

## Project Overview

This project is a LlamaIndex-based application that demonstrates how to build and deploy a Retrieval-Augmented Generation (RAG) system using LlamaIndex Workflows and LlamaDeploy. The application allows users to ask questions about documents and receive answers with citations.

### Key Components

1. **Backend (Python)**: Uses LlamaIndex to create a workflow that can query documents
2. **Frontend (TypeScript)**: Provides a chat interface using LlamaIndexServer
3. **Deployment**: Uses LlamaDeploy to manage the workflow deployment
4. **Data**: Contains documents (PDFs) that are indexed and searchable

## Prerequisites

1. **Python 3.11-3.13**: Required for the backend
2. **uv**: A fast Python package installer
3. **Node.js and npm**: Required for the frontend
4. **OpenAI API Key or DeepSeek API Key**: Required for LLM and embeddings

### Installing uv

If you don't have uv installed, follow the instructions at: https://docs.astral.sh/uv/getting-started/installation/

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd create-llama-test
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root directory with your API key.

**For OpenAI:**
```bash
# .env (in project root)
OPENAI_API_KEY=your_openai_api_key_here
MODEL=gpt-4.1  # Default: gpt-4.1
EMBEDDING_MODEL=text-embedding-3-large  # Default: text-embedding-3-large
```

**For DeepSeek:**
```bash
# .env (in project root)
OPENAI_API_KEY=your_deepseek_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com
MODEL=deepseek-chat
EMBEDDING_MODEL=text-embedding-3-large
```

### 3. Install Dependencies

```bash
# Install Python dependencies
uv sync

# Install Node.js dependencies (for the UI)
cd ui
npm install
cd ..
```

### 4. Generate Document Index

Before running the application, you need to index the documents:

```bash
uv run generate
```

This command:
- Reads documents from the `ui/data` directory (currently contains 101.pdf)
- Creates embeddings for each document
- Stores the index for later use

## Running the Application

The application requires two processes to be running simultaneously:

### Step 1: Start the LlamaDeploy API Server

In a terminal, run:

```bash
uv run -m llama_deploy.apiserver
```

You should see output like:
```
INFO:     Started server process [10842]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:4501 (Press CTRL+C to quit)
```

### Step 2: Deploy the Workflow

In a second terminal, run:

```bash
uv run llamactl deploy llama_deploy.yml
```

You should see:
```
Deployment successful: chat
```

### Step 3: Access the Application

Once both processes are running, you can access the application in two ways:

1. **Web UI**: Open your browser and navigate to http://localhost:4501/deployments/chat/ui
2. **API Documentation**: Visit http://localhost:4501/docs to see available API endpoints

## Using the Application

### Web Interface

1. Open http://localhost:4501/deployments/chat/ui in your browser
2. Type questions about the documents in the chat interface
3. The system will provide answers with citations from the source documents

### API Usage

You can also interact with the system programmatically:

1. Create a new task:
```bash
curl -X POST 'http://localhost:4501/deployments/chat/tasks/create' \
  -H 'Content-Type: application/json' \
  -d '{
    "input": "{\"user_msg\":\"What is this document about?\",\"chat_history\":[]}",
    "service_id": "workflow"
  }'
```

2. Stream events (replace task_id and session_id with values from the response):
```bash
curl 'http://localhost:4501/deployments/chat/tasks/{task_id}/events?session_id={session_id}&raw_event=true' \
  -H 'Content-Type: application/json'
```

## Customization

### Adding New Documents

1. Place your documents (PDF, DOCX, etc.) in the `ui/data` directory
2. Re-run the indexing process:
   ```bash
   uv run generate
   ```
3. Restart the deployment if needed

### Modifying the Workflow

The workflow logic is defined in `src/workflow.py`. You can modify this file to:
- Change the system prompt
- Add new tools
- Adjust the agent behavior

### Customizing the UI

The UI configuration is in `ui/index.ts`. You can:
- Modify starter questions
- Add custom components
- Change the layout

## Troubleshooting

### Common Issues

1. **"Index not found" error**: Make sure you've run `uv run generate` to index the documents
2. **"OPENAI_API_KEY is missing"**: Check that your `.env` file is in the project root directory and contains a valid API key (for either OpenAI or DeepSeek)
3. **Port conflicts**: Make sure ports 4501 and 3000 are available

### Resetting the Application

If you need to start fresh:

1. Stop all running processes
2. Delete the generated index (usually in a `storage` directory)
3. Re-run the setup process from the beginning

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │  LlamaDeploy    │    │   LlamaIndex    │
│                 │    │   API Server    │    │    Workflow     │
│  (Chat UI)      │◄──►│   (Port 4501)   │◄──►│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Document Index │
                       │   (Vector DB)   │
                       └─────────────────┘
```

## Additional Resources

- [LlamaIndex Documentation](https://docs.llamaindex.ai)
- [Workflows Introduction](https://docs.llamaindex.ai/en/stable/understanding/workflows/)
- [LlamaDeploy GitHub Repository](https://github.com/run-llama/llama_deploy)
- [Chat-UI Documentation](https://ts.llamaindex.ai/docs/chat-ui)