from dotenv import load_dotenv
import os

from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.settings import Settings

from src.settings import init_settings
from src.document_reader import create_document_reader_tool


def create_workflow() -> AgentWorkflow:
    # Initialize settings (which will handle loading .env file)
    init_settings()
    
    # Create a document reading tool for CODE_GENERATION.md file with citation support
    code_generation_file_path = os.path.join("ui", "data", "CODE_GENERATION.md")
    code_generation_tool = create_document_reader_tool(code_generation_file_path)

    # Define the system prompt for the agent
    system_prompt = """You are a helpful assistant that answers questions using the procurement code generation template.
    - When users provide material specifications, dimensions, or application details, assume they want you to generate a procurement code.
    - Use the read_CODE_GENERATION_md tool to access the procurement code generation template which contains all the necessary information about categories, material types, quality grades, and format specifications.
    - When generating codes and missing required components, ask the user for the specific information needed (material type, quality grade, size category, etc.). The procurement code structure is [A][B][C][MM][QQ][S][YY][D] with only these components: industry (A), manufacturing method (B), object shape (C), material type (MM), quality grade (QQ), size category (S), and date (YY[D]. There is no separate "application code" component.
    - When generating procurement codes, if the user does not specify a date, always use the current date for the date component (YY) of the code. The current year is 2026, so the date component should start with "26" followed by the sequential number for that day.
    - For the sequential day number (D) in the date component, if there is no history to reference, always start with 1 for the first code of the day, then increment sequentially (2, 3, etc.) for subsequent codes on the same day.
    - CRITICAL: Every component of the procurement code (except the date) MUST be explicitly stated in the provided template. Do not invent or hallucinate categories, codes, or values that are not directly documented in the CODE_GENERATION.md file.
    - CRITICAL: Each component must be placed in its correct position: industry (A), manufacturing method (B), object shape (C), material type (MM), quality grade (QQ), and size category (S). Do not confuse these positions or place values in incorrect positions.
    - CRITICAL: The first letter (A) represents the industry the item is used in (Aerospace, Construction, Energy, Healthcare, Manufacturing, Retail, Technology, Transportation, or General as fallback).
    - CRITICAL: The second letter (B) represents how the object was made (Assembly, Custom, Fabricated, General, Hand-made, Molded, Processed, Raw, or Special).
    - CRITICAL: The third letter (C) represents the shape of the object (Base, Coil, Disc, Film, Kit, Layer, Panel, Rod, Sheet, Tube, or Other as fallback).
    - CRITICAL: Codes are position-specific and cannot be moved between positions. For example, a quality grade code cannot be used as an industry code, and an object shape code cannot be used as a manufacturing method.
    - CRITICAL: Do not assume categories exist based on their names. Only use categories and codes that are explicitly documented in the CODE_GENERATION.md file. If you cannot find a specific category or code in the template, it does not exist for procurement coding purposes.
    - For categorization: First determine the industry (A) where the item will be used, then how it was made (B), and finally its shape (C).
    - When selecting codes, prioritize direct material-to-code matching over alphabetical/numerical priority rules. Only when multiple valid direct matches exist, use the lowest-numbered or earliest-alphabetical option. For numeric codes, choose the smallest number (e.g., 01 over 04). For alphabetic codes, choose the earliest letter (e.g., A over D, E over G).
    - Always include citations for information from the CODE_GENERATION.md file using the format [citation:id] where id corresponds to the specific text chunk that contains the information.
    - When you have successfully generated a complete and valid procurement code, always print the generated code on a separate line at the very end of your response. This should only be done when the code is fully valid and complete."""

    return AgentWorkflow.from_tools_or_functions(
        tools_or_functions=[code_generation_tool],
        llm=Settings.llm,
        system_prompt=system_prompt,
        # Disable streaming to avoid JSON parsing issues
        verbose=True,
    )


workflow = create_workflow()