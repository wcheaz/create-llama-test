import os
from typing import Any, Optional

from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.indices.base import BaseIndex
from llama_index.core.tools.query_engine import QueryEngineTool


def create_query_engine(index: BaseIndex, **kwargs: Any) -> BaseQueryEngine:
    """
    Create a query engine for the given index.

    Args:
        index: The index to create a query engine for.
        params (optional): Additional parameters for the query engine, e.g: similarity_top_k
    """
    top_k = int(os.getenv("TOP_K", 1))  # Default to 5 if not set
    # Only set similarity_top_k if not already specified in kwargs
    if "similarity_top_k" not in kwargs and top_k > 0:
        kwargs["similarity_top_k"] = top_k

    # Log the RAG query parameters for debugging
    print("\n" + "="*80)
    print("🔍 RAG QUERY ENGINE PARAMETERS START")
    print("="*80)
    print(f"Top K: {top_k}")
    print(f"Additional kwargs: {kwargs}")
    print("="*80)
    print("🏁 RAG QUERY ENGINE PARAMETERS END")
    print("="*80 + "\n")
    
    # Also write to log file
    import time
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("llm_prompts.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] RAG QUERY ENGINE PARAMETERS:\n")
        f.write(f"{'-'*60}\n")
        f.write(f"Top K: {top_k}\n")
        f.write(f"Additional kwargs: {kwargs}\n")
        f.write(f"{'-'*60}\n\n")

    return index.as_query_engine(**kwargs)


def get_query_engine_tool(
    index: BaseIndex,
    name: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs: Any,
) -> QueryEngineTool:
    """
    Get a query engine tool for the given index.

    Args:
        index: The index to create a query engine for.
        name (optional): The name of the tool.
        description (optional): The description of the tool.
    """
    if name is None:
        name = "query_index"
    if description is None:
        description = "Use this tool to retrieve information from a knowledge base. Provide a specific query and can call the tool multiple times if necessary."
    query_engine = create_query_engine(index, **kwargs)
    tool = QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name=name,
        description=description,
    )
    return tool
