from dotenv import load_dotenv

from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.settings import Settings

from src.index import get_index
from src.query import get_query_engine_tool
from src.citation import CITATION_SYSTEM_PROMPT, enable_citation
from src.settings import init_settings


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

    # Define the system prompt for the agent
    # Append the citation system prompt to the system prompt
    system_prompt = """You are a helpful assistant that ONLY answers questions using information from the provided knowledge base.
    - You must NOT use any general knowledge or information outside of the knowledge base.
    - If the information is not available in the knowledge base, respond with "I cannot find information about this topic in the provided knowledge base."
    - Always cite your sources using the citation format provided.
    - Do not make up, infer, or extrapolate information that is not explicitly stated in the knowledge base."""
    system_prompt += CITATION_SYSTEM_PROMPT

    return AgentWorkflow.from_tools_or_functions(
        tools_or_functions=[query_tool],
        llm=Settings.llm,
        system_prompt=system_prompt,
    )


workflow = create_workflow()
