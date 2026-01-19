import os
import time
from typing import Any, Dict, List, Optional, Sequence, Union

from llama_index.core.base.llms.types import (
    ChatMessage,
    ChatResponse,
    CompletionResponse,
    LLMMetadata,
)
from llama_index.core.llms.callbacks import llm_chat_callback, llm_completion_callback
from llama_index.core.llms import CustomLLM
from llama_index.llms.deepseek import DeepSeek


class LoggingLLM(CustomLLM):
    """
    A wrapper around DeepSeek LLM that logs all prompts and responses to the console.
    This helps with debugging by showing exactly what prompts are being sent to the LLM.
    """

    context_window: int = 128000  # DeepSeek-chat max context length
    num_output: int = 4096
    model_name: str = "deepseek-chat"
    is_chat_model: bool = True
    log_file: str = "llm_prompts.log"  # Add log_file as a field

    def __init__(self, **kwargs: Any) -> None:
        # Initialize log_file before calling super().__init__ to avoid field validation issues
        kwargs.setdefault("log_file", "llm_prompts.log")
        super().__init__(**kwargs)
        
        # Initialize the actual DeepSeek LLM
        api_key = os.getenv("DEEPSEEK_API_KEY")
        api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
        model = os.getenv("MODEL", "deepseek-chat")
        
        self._llm = DeepSeek(
            model=model,
            api_key=api_key,
            api_base=api_base,
            streaming=False,
        )
        self.model_name = model
        
        # Initialize log file
        self._init_log_file()

    def _init_log_file(self) -> None:
        """Initialize the log file with a header."""
        with open(self.log_file, "a", encoding="utf-8") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n{'='*60}\n")
            f.write(f"LLM Prompt Logging Session - {timestamp}\n")
            f.write(f"{'='*60}\n\n")

    def _write_to_log(self, content: str, entry_type: str) -> None:
        """Write content to the log file with a timestamp and entry type."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {entry_type}:\n")
            f.write(f"{'-'*60}\n")
            f.write(f"{content}\n")
            f.write(f"{'-'*60}\n\n")

    @property
    def metadata(self) -> LLMMetadata:
        """Get LLM metadata."""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model_name,
        )

    def _log_prompt(self, prompt: str, prompt_type: str = "Completion") -> None:
        """Log a prompt to the console with clear markers."""
        print("\n" + "="*80)
        print(f"🚀 {prompt_type} PROMPT START")
        print("="*80)
        print(prompt)
        print("="*80)
        print(f"🏁 {prompt_type} PROMPT END")
        print("="*80 + "\n")
        
        # Also write to log file
        self._write_to_log(prompt, f"{prompt_type} PROMPT")

    def _log_chat_messages(self, messages: Sequence[ChatMessage]) -> None:
        """Log chat messages to the console with clear markers."""
        print("\n" + "="*80)
        print("💬 CHAT MESSAGES START")
        print("="*80)
        for i, message in enumerate(messages):
            role = message.role.upper()
            print(f"\n--- Message {i+1} ({role}) ---")
            print(message.content)
        print("="*80)
        print("🏁 CHAT MESSAGES END")
        print("="*80 + "\n")
        
        # Also write to log file
        formatted_messages = "\n".join([f"Message {i+1} ({message.role.upper()}): {message.content}" for i, message in enumerate(messages)])
        self._write_to_log(formatted_messages, "CHAT MESSAGES")

    def _log_response(self, response: str, response_type: str = "Completion") -> None:
        """Log a response to the console with clear markers."""
        print("\n" + "="*80)
        print(f"📤 {response_type} RESPONSE START")
        print("="*80)
        print(response)
        print("="*80)
        print(f"🏁 {response_type} RESPONSE END")
        print("="*80 + "\n")
        
        # Also write to log file
        self._write_to_log(response, f"{response_type} RESPONSE")

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """Complete the prompt and log both input and output."""
        self._log_prompt(prompt, "COMPLETION")
        
        # Get the actual response from DeepSeek
        response = self._llm.complete(prompt, **kwargs)
        
        self._log_response(response.text, "COMPLETION")
        return response

    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        """Chat with the messages and log both input and output."""
        self._log_chat_messages(messages)
        
        # Get the actual response from DeepSeek
        response = self._llm.chat(messages, **kwargs)
        
        self._log_response(response.message.content or "", "CHAT")
        return response

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any):
        """Stream complete the prompt and log both input and output."""
        self._log_prompt(prompt, "STREAM COMPLETION")
        
        # Get the actual streaming response from DeepSeek
        response_generator = self._llm.stream_complete(prompt, **kwargs)
        
        # Collect the full response for logging
        full_response = ""
        for chunk in response_generator:
            full_response += chunk.delta
            yield chunk
        
        self._log_response(full_response, "STREAM COMPLETION")

    @llm_chat_callback()
    def stream_chat(self, messages: Sequence[ChatMessage], **kwargs: Any):
        """Stream chat with the messages and log both input and output."""
        self._log_chat_messages(messages)
        
        # Get the actual streaming response from DeepSeek
        response_generator = self._llm.stream_chat(messages, **kwargs)
        
        # Collect the full response for logging
        full_response = ""
        for chunk in response_generator:
            full_response += chunk.delta
            yield chunk
        
        self._log_response(full_response, "STREAM CHAT")