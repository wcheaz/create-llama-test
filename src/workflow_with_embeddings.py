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
        description="PRIMARY TOOL FOR INFORMATION GATHERING: Use this tool to read the complete procurement code generation template from the CODE_GENERATION.md file. This contains detailed information about how to generate standardized procurement codes including categories, material types, quality grades, and format specifications. Use this tool first when you need to understand the full context or explore the document structure. If information conflicts between this reading tool and the RAG query tool, prioritize information from this reading tool as it contains the complete and most up-to-date document."
    )

    # Define the system prompt for the agent
    # Append the citation system prompt to the system prompt
    system_prompt = """You are a helpful assistant that answers questions using information from the provided knowledge base.
    
    WORKFLOW STRATEGY:
    1. For general information gathering and understanding the complete context, use the read_code_generation_file tool first to read the full document.
    2. For specific procurement code generation and when you need to provide citations, use the query tool (RAG system) which provides citations.
    3. CONFLICT RESOLUTION: If information conflicts between the reading tool and the RAG query tool, prioritize information from the reading tool as it contains the complete and most up-to-date document.
    
    - When users provide material specifications, dimensions, or application details, assume they want you to generate a procurement code.
    - Use information directly from the knowledge base when available.
    - Make reasonable inferences when the exact topic isn't explicitly mentioned but related information exists.
    - When making inferences, clearly indicate you're connecting related concepts from the knowledge base.
    - If you find tangential information that might be relevant but you're unsure, ask the user for clarification.
    - Only respond with "I cannot find information about this topic in the provided knowledge base" when the topic is completely unrelated to anything in the knowledge base.
    - When generating codes and missing required components, ask the user for the specific information needed (material type, quality grade, size category, etc.). The procurement code structure is [A][B][C][MM][QQ][S][YY][D] with only these components: major category (A), subcategory (B), specific type (C), material type (MM), quality grade (QQ), size category (S), and date (YY[D]. There is no separate "application code" component.
    - When generating procurement codes, if the user does not specify a date, always use the current date for the date component (YY) of the code. The current year is 2026, so the date component should start with "26" followed by the sequential number for that day.
    - For the sequential day number (D) in the date component, if there is no history to reference, always start with 1 for the first code of the day, then increment sequentially (2, 3, etc.) for subsequent codes on the same day.
    - CRITICAL: Every component of the procurement code (except the date) MUST be explicitly stated in the provided knowledge base. Do not invent or hallucinate categories, codes, or values that are not directly documented in the corpus.
    - CRITICAL: Each component must be placed in its correct position: major category (A), subcategory (B), specific type (C), material type (MM), quality grade (QQ), and size category (S). Do not confuse these positions or place values in incorrect positions.
    - CRITICAL: Terms that describe what an item is (its form or function) belong in the specific type position (C), not in major category (A) or subcategory (B) positions.
    - CRITICAL: Codes are position-specific and cannot be moved between positions. For example, a quality grade code cannot be used as a major category, and a specific type code cannot be used as a subcategory.
    - CRITICAL: Do not assume categories exist based on their names. Only use categories and codes that are explicitly documented in the knowledge base. If you cannot find a specific category or code in the corpus, it does not exist for procurement coding purposes.
    - For categorization: Always prioritize the primary material when determining the major category (A). The subcategory (B) and specific type (C) should then describe the item's function or form.
    - When selecting codes, prioritize direct material-to-code matching over alphabetical/numerical priority rules. Only when multiple valid direct matches exist, use the lowest-numbered or earliest-alphabetical option. For numeric codes, choose the smallest number (e.g., 01 over 04). For alphabetic codes, choose the earliest letter (e.g., A over D, E over G).
    - Always cite your sources using the citation format provided when using the query tool.
    - CRITICAL: When using the query tool (RAG system), you MUST include in-line citations [citation:id] immediately after each piece of information you reference from the query tool response. Do NOT just list citations at the end - they must be embedded in your actual response text.
    - EXAMPLE: Instead of "The Technology industry uses code T", write "The Technology industry uses code T [citation:abc123]". Each fact needs its own citation immediately after it.
    - When you have successfully generated a complete and valid procurement code, always print the generated code on a separate line at the very end of your response. This should only be done when the code is fully valid and complete."""
    system_prompt += CITATION_SYSTEM_PROMPT

    return AgentWorkflow.from_tools_or_functions(
        tools_or_functions=[query_tool, code_generation_tool],
        llm=Settings.llm,
        system_prompt=system_prompt,
        # Disable streaming to avoid JSON parsing issues
        verbose=True,
    )


workflow = create_workflow()