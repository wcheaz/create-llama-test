import os
import datetime
from typing import Any, Dict, List, Optional
from llama_index.core.callbacks.base import BaseCallbackHandler
from llama_index.core.callbacks.schema import CBEventType, EventPayload

class LLMDebugHandler(BaseCallbackHandler):
    """
    Callback handler to log LLM inputs and outputs to a file for debugging context issues.
    """
    def __init__(
        self, 
        log_file: str = "hidden/LLM-TEXT.log", 
        error_file: str = "hidden/LLM-TEXT-ERRORS.log",
        context_window: int = 128000
    ) -> None:
        super().__init__(event_starts_to_ignore=[], event_ends_to_ignore=[])
        self.log_file = log_file
        self.error_file = error_file
        self.context_window = context_window
        self.call_count = 0
        
        # Ensure hidden directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Clear/Create logs on init
        with open(self.log_file, "a") as f:
            f.write(f"\n{'='*20} NEW SESSION {datetime.datetime.now().isoformat()} {'='*20}\n")

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        if event_type == CBEventType.LLM and payload:
            self.call_count += 1
            messages = payload.get(EventPayload.MESSAGES, [])
            prompt = payload.get(EventPayload.PROMPT, "")
            
            # Format content
            log_content = f"\n\n--- Call #{self.call_count} START at {datetime.datetime.now().isoformat()} ---\n"
            
            total_chars = 0
            
            if messages:
                log_content += "Type: Chat Messages\n"
                for i, msg in enumerate(messages):
                    role = getattr(msg, "role", "unknown")
                    content = getattr(msg, "content", "")
                    
                    # Handle case where content might be blocks/chunks (LlamaIndex specific)
                    if not isinstance(content, str):
                        content = str(content)
                        
                    log_content += f"[{i}] Role: {role}\nContent:\n{content}\n{'-'*20}\n"
                    total_chars += len(content)
            elif prompt:
                log_content += f"Type: Completion Prompt\nContent:\n{prompt}\n"
                total_chars += len(prompt)
                
            # Log to main file
            with open(self.log_file, "a") as f:
                f.write(log_content)
                
            # Overflow check (Approximation: 1 token ~= 4 chars)
            estimated_tokens = total_chars / 4
            if estimated_tokens > self.context_window:
                error_msg = (
                    f"POTENTIAL OVERFLOW: Call #{self.call_count} input estimated at {estimated_tokens:.0f} tokens "
                    f"(Context Window: {self.context_window})\n"
                )
                with open(self.error_file, "a") as f:
                    f.write(f"[{datetime.datetime.now().isoformat()}] {error_msg}")
                    
        return event_id

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        if event_type == CBEventType.LLM and payload:
            response = payload.get(EventPayload.RESPONSE)
            # Response might be a Response object or string depending on completion/chat
            response_text = str(response)
            
            log_content = f"\n--- Call #{self.call_count} END ---\nResponse:\n{response_text}\n{'='*40}\n"
            
            with open(self.log_file, "a") as f:
                f.write(log_content)

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        pass

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        pass
