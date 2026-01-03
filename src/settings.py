import os
from pathlib import Path

from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI


def init_settings():
    # Load .env from project root
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    if os.getenv("OPENAI_API_KEY") is None:
        raise RuntimeError("OPENAI_API_KEY is missing in environment variables")
    
    # Configure LLM with optional base URL for DeepSeek
    llm_kwargs = {"model": os.getenv("MODEL") or "gpt-4.1"}
    if base_url := os.getenv("OPENAI_BASE_URL"):
        llm_kwargs["api_base"] = base_url
    Settings.llm = OpenAI(**llm_kwargs)
    
    # Configure embedding model with optional base URL for DeepSeek
    embed_kwargs = {"model": os.getenv("EMBEDDING_MODEL") or "text-embedding-3-large"}
    if base_url := os.getenv("OPENAI_BASE_URL"):
        embed_kwargs["api_base"] = base_url
    Settings.embed_model = OpenAIEmbedding(**embed_kwargs)
