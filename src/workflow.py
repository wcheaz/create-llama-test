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
    system_prompt = """You are a helpful assistant that answers questions using information from the provided knowledge base.
    - Use information directly from the knowledge base when available.
    - Make reasonable inferences when the exact topic isn't explicitly mentioned but related information exists. For example, if a specific application isn't mentioned but the material properties are, you can infer how the material might be used.
    - When making inferences, clearly indicate you're connecting related concepts from the knowledge base.
    - If you find tangential information that might be relevant but you're unsure, ask the user for clarification about whether the related information would be helpful.
    - Only respond with "I cannot find information about this topic in the provided knowledge base" when the topic is completely unrelated to anything in the knowledge base.
    - When generating codes and you cannot determine all required components from the knowledge base, ask the user to provide the missing information. For procurement codes, query for specific categories like material type, quality grade, size category, or other missing components needed to complete the code.
    - Always cite your sources using the citation format provided."""
    system_prompt += CITATION_SYSTEM_PROMPT

    return AgentWorkflow.from_tools_or_functions(
        tools_or_functions=[query_tool],
        llm=Settings.llm,
        system_prompt=system_prompt,
    )


workflow = create_workflow()
