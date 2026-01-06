import os

from llama_index.core import Settings
from llama_index.llms.deepseek import DeepSeek
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def load_env_file(env_path):
    """Manually load environment variables from .env file"""
    if not os.path.exists(env_path):
        return False
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                os.environ[key] = value
    return True


def init_settings():
    # Check for DeepSeek API key in environment
    if os.getenv("DEEPSEEK_API_KEY") is None:
        # Try to load from .env file in current directory
        current_dir = os.getcwd()
        env_file = os.path.join(current_dir, '.env')
        
        if not os.path.exists(env_file):
            # Try project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            env_file = os.path.join(project_root, '.env')
        
        if os.path.exists(env_file):
            # Manually load the .env file
            if load_env_file(env_file):
                if os.getenv("DEEPSEEK_API_KEY") is None:
                    raise RuntimeError(f"DEEPSEEK_API_KEY is missing in environment variables after loading {env_file}")
            else:
                raise RuntimeError(f"Failed to load .env file from {env_file}")
        else:
            raise RuntimeError(f"DEEPSEEK_API_KEY is missing in environment variables. No .env file found at {env_file}")
    
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
