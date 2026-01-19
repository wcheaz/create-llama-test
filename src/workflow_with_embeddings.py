from dotenv import load_dotenv
import os

from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.settings import Settings
from llama_index.core.tools import FunctionTool

from src.index import get_index
from src.query import get_query_engine_tool
from src.citation import CITATION_SYSTEM_PROMPT, enable_citation
from src.settings import init_settings


def read_code_generation_file() -> str:
    """
    Read the contents of the CODE_GENERATION.md file which contains the procurement code generation template.
    
    Returns:
        The contents of the CODE_GENERATION.md file as a string
    """
    try:
        file_path = os.path.join("ui", "data", "CODE_GENERATION.md")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading CODE_GENERATION.md file: {str(e)}"
# In src/workflow.py

def create_workflow() -> AgentWorkflow:
    # Initialize settings (which will handle loading .env file)
    init_settings()
    index = get_index()
    if index is None:
        raise RuntimeError(
            "Index not found! Please run `uv run generate` to index the data first."
        )
    # Create a query tool with citations enabled
    query_tool = enable_citation(get_query_engine_tool(index=index))
    
    # Create a file reading tool for the CODE_GENERATION.md file
    code_generation_tool = FunctionTool.from_defaults(
        fn=read_code_generation_file,
        name="read_code_generation_file",
        description="PRIMARY TOOL: Reads the procurement code generation rules."
    )

    # --- THE FIX IS HERE ---
    # We removed the massive text block. This prevents the browser stream from crashing.
    system_prompt = """You are a helpful assistant for procurement code generation.

    CRITICAL WORKFLOW:
    1. INITIALIZATION: Your FIRST action must always be to use the tool 'read_code_generation_file'. 
       - This file contains the Master Rules for codes, categories, and formatting.
       - Do not attempt to generate codes until you have read this file.
    
    2. EXECUTION:
       - Strictly follow the logic defined in the CODE_GENERATION.md file you just read.
       - Use the query tool for specific citations if needed.
       - If the user implies a procurement request, generate the code following the file's instructions.
       - Use the current date (2026) if unspecified.
       - Always provide inline citations [citation:id].
    """
    system_prompt += CITATION_SYSTEM_PROMPT

    return AgentWorkflow.from_tools_or_functions(
        tools_or_functions=[query_tool, code_generation_tool],
        llm=Settings.llm,
        system_prompt=system_prompt,
        verbose=True,
    )

workflow = create_workflow()