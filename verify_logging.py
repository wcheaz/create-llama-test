import asyncio
import os
from dotenv import load_dotenv
# Add src to path if needed, usually running from root works
import sys
sys.path.append(os.getcwd())

from src.workflow_with_embeddings import workflow

load_dotenv()

async def main():
    print("Running verification query...")
    try:
        # Run a simple query to trigger LLM calls
        handler = workflow.run(user_msg="Hello, this is a test to verify logging.")
        # handler is a WorkflowHandler, we need to await the result or iterate events?
        # AgentWorkflow.run typically returns a specific handler or the result if run directly?
        # Actually in LlamaIndex Workflows, .run() returns a WorkflowHandler usually.
        # But AgentWorkflow might be different. Let's assume standard async run behavior.
        # If it returns a handler, we await it.
        result = await handler
        print(f"Response received: {str(result)}")
    except Exception as e:
        print(f"Error running workflow: {e}")

if __name__ == "__main__":
    asyncio.run(main())
