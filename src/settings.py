import os

from llama_index.core import Settings
from llama_index.llms.deepseek import DeepSeek
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def init_settings():
    # Check for DeepSeek API key
    if os.getenv("DEEPSEEK_API_KEY") is None:
        raise RuntimeError("DEEPSEEK_API_KEY is missing in environment variables")
    
    # Initialize DeepSeek LLM
    Settings.llm = DeepSeek(
        model=os.getenv("MODEL") or "deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        api_base=os.getenv("DEEPSEEK_API_BASE") or "https://api.deepseek.com"
    )
    
    # Initialize HuggingFace embeddings (using the BAAI model from your .env)
    Settings.embed_model = HuggingFaceEmbedding(
        model_name=os.getenv("EMBEDDING_MODEL") or "BAAI/bge-large-en-v1.5"
    )
