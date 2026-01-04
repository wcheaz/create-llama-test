import os
from pathlib import Path

from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import LLMMetadata


class DeepSeekOpenAI(OpenAI):
    """Custom OpenAI class that bypasses model validation for DeepSeek"""
    
    def __init__(self, **kwargs):
        # Ensure context_window is set for DeepSeek
        if "context_window" not in kwargs:
            kwargs["context_window"] = 128000
        super().__init__(**kwargs)
    
    @property
    def metadata(self) -> LLMMetadata:
        """Override metadata to avoid model validation for DeepSeek"""
        # Get the base metadata but skip the model name validation
        return LLMMetadata(
            context_window=128000,  # Use DeepSeek's context window
            num_output=getattr(self, 'num_output', 4096),
            is_chat_model=True,  # DeepSeek-chat is a chat model
            is_function_calling_model=True,
            model_name="deepseek-chat",  # Use the actual model name
            system_role="system",
        )


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
    actual_model_name = os.getenv("MODEL") or "deepseek-chat"
    llm_kwargs = {"model": actual_model_name}
    
    if base_url := os.getenv("OPENAI_BASE_URL"):
        llm_kwargs["api_base"] = base_url
        # For custom API endpoints like DeepSeek, we need to set the context window manually
        if "deepseek" in base_url.lower():
            llm_kwargs["context_window"] = 128000  # DeepSeek context window
            # Use our custom OpenAI class for DeepSeek to bypass model validation
            Settings.llm = DeepSeekOpenAI(**llm_kwargs)
        else:
            Settings.llm = OpenAI(**llm_kwargs)
    else:
        Settings.llm = OpenAI(**llm_kwargs)
    
    # Configure Hugging Face embedding model
    embed_model_name = os.getenv("EMBEDDING_MODEL") or "BAAI/bge-large-en-v1.5"
    embed_device = os.getenv("EMBEDDING_DEVICE") or "cpu"
    
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=embed_model_name,
        device=embed_device,
        embed_batch_size=32
    )
