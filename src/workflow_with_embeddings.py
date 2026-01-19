from dotenv import load_dotenv
import os
import random
import datetime
import logging
import time

# Standard imports
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.settings import Settings
from llama_index.core.tools import FunctionTool

# Project imports
from src.index import get_index
from src.query import get_query_engine_tool
from src.citation import CITATION_SYSTEM_PROMPT, enable_citation
from src.settings import init_settings

# --- 1. Token Generation Logic ---
def generate_human_readable_token():
    colors = ["RED", "BLUE", "GREEN", "PURPLE", "ORANGE", "GOLD"]
    animals = ["EAGLE", "TIGER", "BEAR", "WOLF", "HAWK", "LION"]
    number = random.randint(100, 999)
    # Example: "GOLD-LION-482" - The LLM cannot guess this.
    return f"{random.choice(colors)}-{random.choice(animals)}-{number}"

def read_code_generation_file() -> str:
    try:
        file_path = os.path.join("ui", "data", "CODE_GENERATION.md")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # We generate a fresh token every time this function is called
        auth_token = generate_human_readable_token()
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # We wrap the content in a "Security Header"
        header = (
            f"!!! SECURITY CHECK PASSED !!!\n"
            f"ACTIVE SESSION TOKEN: {auth_token}\n"
            f"SERVER TIME: {timestamp}\n"
            f"INSTRUCTION: You are authorized to generate a code using the rules below.\n"
            f"MANDATORY: You MUST cite the token '{auth_token}' in your final response.\n"
            f"------------------------------------------------\n\n"
        )
        
        full_content = header + content
        
        # Log the code generation file content for debugging
        print("\n" + "="*80)
        print("🔐 CODE GENERATION FILE CONTENT START")
        print("="*80)
        print(full_content)
        print("="*80)
        print("🏁 CODE GENERATION FILE CONTENT END")
        print("="*80 + "\n")
        
        # Also write to log file
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("llm_prompts.log", "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] CODE GENERATION FILE CONTENT:\n")
            f.write(f"{'-'*60}\n")
            f.write(f"{full_content}\n")
            f.write(f"{'-'*60}\n\n")
        
        return full_content
    except Exception as e:
        return f"Error: {str(e)}"

# --- 2. Workflow Creation ---
def create_workflow() -> AgentWorkflow:
    init_settings()
    index = get_index()
    if index is None:
        raise RuntimeError("Index not found! Run `uv run generate` first.")
    
    # 1. THE RESTRICTED QUERY TOOL
    # We explicitly tell the agent this tool is useless for generating codes.
    query_tool = enable_citation(get_query_engine_tool(
        index=index,
        description=(
            "RESTRICTED: Use ONLY for historical definitions (e.g., 'What is Inconel?'). "
            "DO NOT USE THIS TOOL FOR PROCUREMENT CODES or CATEGORIES. "
            "This tool does not have the Auth Token."
        )
    ))
    
    # 2. THE MANDATORY AUTH TOOL
    # Renaming it to "get_mandatory_auth_token" changes the agent's perception of the tool 
    # from "Reading a file" (Optional) to "Logging In" (Required).
    code_generation_tool = FunctionTool.from_defaults(
        fn=read_code_generation_file,
        name="get_mandatory_auth_token",
        description=(
            "SECURITY LOCK: This tool grants the 'Session Token' required to generate a code. "
            "You are FORBIDDEN from generating a code without a fresh Token. "
            "Tokens expire immediately. "
            "Input: None. Output: New Token + Code Rules."
        )
    )

    # 3. THE PROMPT STRATEGY
    # We split the prompt. The Security Enforcement goes LAST.
    
    base_prompt = """You are the Procurement Code Governance Agent.

    ### CORE OBJECTIVE
    Your goal is to generate accurate procurement codes.
    However, you operate in a **STATELESS** environment.
    - You have NO MEMORY of previous codes.
    - You have NO MEMORY of the governance rules.
    - You must fetch the rules afresh for every single request.

    ### THE "TOKEN" MECHANISM
    The `get_mandatory_auth_token` tool generates a random phrase like **"RED-EAGLE-999"**.
    - This phrase is RANDOM. You CANNOT guess it.
    - If you invent a token (e.g. "4F3B..." or "SECURE-123"), the system will detect the fraud and block you.
    - **You must call the tool to see the current color/animal combination.**

    ### EXECUTION ALGORITHM (Follow Exactly)
    1. **User Request:** "Generate code for X."
    2. **Blocker:** "I need the Auth Token."
    3. **Action:** Call `get_mandatory_auth_token`.
    4. **STOP:** Wait for the tool output.
    5. **Analysis:** Extract the Token. Verify the Code components.
    6. **Output:** Generate the final response.

    ### FINAL OUTPUT STRUCTURE
    ---
    **Procurement Analysis**
    * **Auth Token:** [COLOR-ANIMAL-NUMBER] <--- MUST MATCH TOOL OUTPUT EXACTLY
    * **Major Category (A):** [Value]
    * **Subcategory (B):** [Value]
    * **Specific Type (C):** [Value]
    * **Material (MM):** [Value]
    * **Quality (QQ):** [Value]
    * **Size (S):** [Value]
    * **Date:** [26][Seq#]

    **Final Code:**
    [CODE]
    ---
    """
    
    # CRITICAL: We append the security reminder AFTER the citation prompt.
    # This ensures the "Rules" are the very last thing the LLM reads before processing the user message.
    final_system_prompt = base_prompt + "\n\n" + CITATION_SYSTEM_PROMPT + """
    
    ### FINAL SECURITY REMINDER
    1. **IGNORE** your internal memory of codes.
    2. **CALL** `get_mandatory_auth_token` immediately.
    3. **VERIFY** the 'Color-Animal' token format.
    """

    # Log the system prompt for debugging
    print("\n" + "="*80)
    print("🔧 WORKFLOW SYSTEM PROMPT START")
    print("="*80)
    print(final_system_prompt)
    print("="*80)
    print("🏁 WORKFLOW SYSTEM PROMPT END")
    print("="*80 + "\n")
    
    # Also write to log file
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("llm_prompts.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] WORKFLOW SYSTEM PROMPT:\n")
        f.write(f"{'-'*60}\n")
        f.write(f"{final_system_prompt}\n")
        f.write(f"{'-'*60}\n\n")

    return AgentWorkflow.from_tools_or_functions(
        tools_or_functions=[query_tool, code_generation_tool],
        llm=Settings.llm,
        system_prompt=final_system_prompt,
    )

workflow = create_workflow()