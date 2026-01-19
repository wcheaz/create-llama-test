#!/usr/bin/env python3
"""
Test script to verify that the LLM logging is working properly.
This script will initialize the workflow and make a simple test query.
"""

import os
import sys
import asyncio

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.workflow_with_embeddings import workflow

async def test_logging():
    """Test that prompts are being logged properly"""
    print("="*80)
    print("TESTING PROMPT LOGGING")
    print("="*80)
    
    # Create a simple test message
    test_message = "Generate a procurement code for a stainless steel bolt used in aerospace industry."
    
    print(f"\nSending test message: {test_message}\n")
    
    # Run the workflow with the test message
    try:
        response = await workflow.run(user_msg=test_message)
        print(f"\nReceived response: {response}\n")
    except Exception as e:
        print(f"\nError during test: {e}\n")
    
    print("="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_logging())