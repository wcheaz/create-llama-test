"""
Debug version of workflow.py with additional logging to identify issues
"""

import logging
from typing import Any, Dict

from dotenv import load_dotenv

from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.settings import Settings
from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step

from src.index import get_index
from src.query import get_query_engine_tool
from src.citation import CITATION_SYSTEM_PROMPT, enable_citation
from src.settings import init_settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatEvent(Event):
    """Custom event for chat messages"""
    msg: str


class DebugWorkflow(Workflow):
    """Debug version of the workflow with logging"""
    
    @step
    async def handle_start(self, ev: StartEvent) -> ChatEvent:
        logger.info(f"Workflow started with input: {ev}")
        
        # Initialize settings and index
        load_dotenv()
        init_settings()
        index = get_index()
        if index is None:
            logger.error("Index not found!")
            raise RuntimeError(
                "Index not found! Please run `uv run generate` to index data first."
            )
        
        logger.info("Index loaded successfully")
        
        # Extract user message from input
        input_data = ev.get("input", {})
        if isinstance(input_data, str):
            input_data = {"user_msg": input_data}
        
        user_msg = input_data.get("user_msg", "")
        logger.info(f"User message: {user_msg}")
        
        return ChatEvent(msg=user_msg)
    
    @step
    async def handle_chat(self, ev: ChatEvent) -> StopEvent:
        logger.info(f"Processing chat event: {ev.msg}")
        
        # Get index (should be cached from first step)
        index = get_index()
        
        # Create query tool with citations enabled
        query_tool = enable_citation(get_query_engine_tool(index=index))
        
        # Create a simple agent workflow for this query
        system_prompt = """You are a helpful assistant"""
        system_prompt += CITATION_SYSTEM_PROMPT
        
        agent = AgentWorkflow.from_tools_or_functions(
            tools_or_functions=[query_tool],
            llm=Settings.llm,
            system_prompt=system_prompt,
        )
        
        # Run the agent
        logger.info("Running agent to generate response")
        response = await agent.run(msg=ev.msg)
        logger.info(f"Agent response generated: {str(response)[:100]}...")
        
        return StopEvent(result=response)
    
    @step
    async def handle_stop(self, ev: StopEvent) -> StopEvent:
        logger.info(f"Stop event received: {ev}")
        return ev


def create_debug_workflow() -> Workflow:
    """Create the debug workflow instance"""
    return DebugWorkflow()


# Keep the original workflow for comparison
def create_workflow() -> AgentWorkflow:
    load_dotenv()
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
    system_prompt = """You are a helpful assistant"""
    system_prompt += CITATION_SYSTEM_PROMPT

    return AgentWorkflow.from_tools_or_functions(
        tools_or_functions=[query_tool],
        llm=Settings.llm,
        system_prompt=system_prompt,
    )


# Create both workflow instances
workflow = create_workflow()
debug_workflow = create_debug_workflow()