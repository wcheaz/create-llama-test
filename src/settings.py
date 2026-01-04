import os
from pathlib import Path

from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
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
    model_name = os.getenv("MODEL") or "gpt-4.1"
    llm_kwargs = {"model": model_name}
    if base_url := os.getenv("OPENAI_BASE_URL"):
        llm_kwargs["api_base"] = base_url
        # For custom API endpoints like DeepSeek, we need to set the context window manually
        if "deepseek" in base_url.lower():
            # Use the actual model name from environment (deepseek-chat)
            # Don't override it with a placeholder
            llm_kwargs["context_window"] = 128000  # DeepSeek context window
    Settings.llm = OpenAI(**llm_kwargs)
    
    # Configure Hugging Face embedding model
    embed_model_name = os.getenv("EMBEDDING_MODEL") or "BAAI/bge-large-en-v1.5"
    embed_device = os.getenv("EMBEDDING_DEVICE") or "cpu"
    
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=embed_model_name,
        device=embed_device,
        embed_batch_size=32
    )
