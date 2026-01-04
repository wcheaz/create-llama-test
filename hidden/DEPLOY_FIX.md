# Deployment Fix Guide

## Problem Description

When attempting to create a deployment using `uv run llamactl deploy llama_deploy.yml`, you encounter a 500 Internal Server Error with the following message:

```
Error: Server error '500 Internal Server Error' for url 'http://localhost:4501/deployments/create?reload=false&local=false&base_path=%2Fhome%2Fncheaz%2Fgit%2Fcreate-llama-test'
```

Additionally, you see a Pydantic warning:
```
/home/ncheaz/git/create-llama-test/.venv/lib/python3.12/site-packages/pydantic/_internal/_generate_schema.py:2249: UnsupportedFieldAttributeWarning: The 'validate_default' attribute with value True was provided to the `Field()` function, which has no effect in the context it was used.
```

## Root Cause Analysis

After investigating, I've identified three main issues:

1. **Missing API Key**: The `.env` file contains a placeholder value for the OpenAI API key:
   ```
   OPENAI_API_KEY=your_deepseek_api_key_here
   ```
   This is not a valid API key, which is causing the deployment to fail.

2. **Pydantic Compatibility Issue**: There's a warning about the `validate_default` attribute in Pydantic, which suggests a version compatibility issue between the installed packages.

3. **Model Name Compatibility**: The DeepSeek model name "deepseek-chat" is not recognized by the OpenAI LLM implementation in LlamaIndex, causing a validation error.

## Solution Steps

### 1. Fix the API Key

Replace the placeholder API key in the `.env` file with a valid DeepSeek API key:

```bash
# Edit the .env file
OPENAI_API_KEY=your_actual_deepseek_api_key_here
```

### 2. Update Package Versions

The Pydantic warning suggests there might be version compatibility issues. Update the dependencies in `pyproject.toml` to ensure compatibility:

```toml
dependencies = [
    "python-dotenv>=1.0.0,<2.0.0",
    "pydantic>=2.11.5",
    "aiostream>=0.5.2,<0.6.0",
    "llama-index-core>=0.12.45,<0.13.0",
    "llama-index-readers-file>=0.4.6,<1.0.0",
    "llama-index-indices-managed-llama-cloud>=0.6.3,<1.0.0",
    "llama-deploy",
    "docx2txt>=0.8,<0.9",
    "llama-index-llms-openai>=0.4.5,<0.5.0",
    "llama-index-embeddings-huggingface>=0.4.0,<0.5.0",
    "sentence-transformers>=2.2.2,<3.0.0",
    "torch>=2.0.0,<3.0.0",
    "transformers>=4.35.0,<5.0.0"
]
```

### 3. Fix Model Name Compatibility

Update the `src/settings.py` file to handle the DeepSeek model name correctly:

```python
# Configure LLM with optional base URL for DeepSeek
model_name = os.getenv("MODEL") or "gpt-4.1"
llm_kwargs = {"model": model_name}
if base_url := os.getenv("OPENAI_BASE_URL"):
    llm_kwargs["api_base"] = base_url
    # For custom API endpoints like DeepSeek, we need to use a compatible model name
    # and set the context window manually
    if "deepseek" in base_url.lower():
        # Use gpt-4.1 as a placeholder model name for compatibility
        # The actual model will be determined by the API endpoint
        llm_kwargs["model"] = "gpt-4.1"
        llm_kwargs["context_window"] = 128000  # DeepSeek context window
Settings.llm = OpenAI(**llm_kwargs)
```

### 4. Reinstall Dependencies

After updating the `pyproject.toml`, reinstall the dependencies:

```bash
uv sync
```

### 5. Restart the API Server

Stop the currently running API server (Ctrl+C in the terminal where it's running) and restart it:

```bash
uv run -m llama_deploy.apiserver
```

### 6. Retry the Deployment

Now try deploying again:

```bash
uv run llamactl deploy llama_deploy.yml
```

## Additional Troubleshooting

If the issue persists:

1. Check that the index has been generated:
   ```bash
   ls -la src/storage
   ```
   If the storage directory is empty or missing, run:
   ```bash
   uv run generate
   ```

2. Verify the API server is running correctly:
   ```bash
   curl http://localhost:4501/docs
   ```

3. Check the API server logs for more detailed error messages.

## Additional Troubleshooting for UI Access

If you encounter a 404 error when trying to access the UI:

1. **Check if the API server is running properly**:
   ```bash
   ps aux | grep llama_deploy.apiserver
   ```

2. **Restart the API server if needed**:
   ```bash
   # Kill any existing processes
   pkill -f "llama_deploy.apiserver"
   
   # Start the API server in the background
   nohup uv run -m llama_deploy.apiserver > apiserver.log 2>&1 &
   
   # Wait for it to start
   sleep 5
   ```

3. **Redeploy to ensure everything is properly set up**:
   ```bash
   uv run llamactl deploy llama_deploy.yml
   ```

4. **Verify UI accessibility**:
   ```bash
   curl -s -I http://localhost:4501/deployments/chat/ui
   ```
   You should see a `HTTP/1.1 200 OK` response.

The UI is served through the API server at port 4501, not directly at port 3000.

## Expected Outcome

After following these steps, the deployment should succeed with the message:
```
Deployment successful: chat
```

You should then be able to access the UI at:
http://localhost:4501/deployments/chat/ui