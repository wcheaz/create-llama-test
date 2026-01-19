#!/usr/bin/env python3
"""
Test script to verify Python debugging setup
"""

import os
import sys

def main():
    print("=== Python Debugging Test ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Add src to path if not already there
    if "${workspaceFolder}/src" not in sys.path and "src" not in sys.path:
        sys.path.insert(0, "src")
    
    # Try importing project modules
    try:
        import settings
        print("✓ Successfully imported settings module")
    except ImportError as e:
        print(f"✗ Failed to import settings module: {e}")
    
    try:
        import workflow_with_embeddings
        print("✓ Successfully imported workflow_with_embeddings module")
    except ImportError as e:
        print(f"✗ Failed to import workflow_with_embeddings module: {e}")
    
    # Set a breakpoint here to test debugging
    print("Set a breakpoint on the next line to test debugging")
    test_var = "Debug test successful!"
    print(f"Test variable: {test_var}")
    
    # Check environment variables
    print("\n=== Environment Variables ===")
    env_vars = ["OPENAI_API_KEY", "MODEL_NAME", "EMBEDDING_MODEL"]
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✓ {var}: {'*' * 10}...{value[-4:]}")
        else:
            print(f"✗ {var}: Not set")

if __name__ == "__main__":
    main()