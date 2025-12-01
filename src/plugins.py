import logging
import time 
import os
from typing import Any, Dict


class FileLoggingPlugin:
    """
    A production-grade plugin to trace agent activities to a file.
    Hooks into:
    1. Agent Execution Start (before_agent)
    2. Model Call Start (before_model)
    3. Tool Execution (before_tool/after_tool)
    """

    def __init__(self, log_file_path: str = "logs/agent_trace.log"):
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        
        # Configure a specific logger for this plugin
        self.logger = logging.getLogger("MediScreenTracer")
        self.logger.setLevel(logging.INFO)
        
        # Very Imporant for Clean UI: This prevents logs from leaking to the main console
        self.logger.propagate = False

        # File Handler
        handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Clear existing handlers to avoid duplicates
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.logger.addHandler(handler)

    def before_agent(self, agent_name: str, input_data: Any) -> None:
        """Called by Runner before handing control to an agent."""
        self.logger.info(f"🏁 [AGENT START] Agent: {agent_name}")
        self.logger.info(f"📥 [INPUT] {input_data}")

    def before_model(self, model_name: str, prompt: Any) -> None:
        """Called before the Agent sends a prompt to Gemini."""
        self.logger.info(f"🤖 [MODEL CALL] Invoking {model_name}...")
        # Optional: Log full prompt if debugging (be careful with PII)
        # self.logger.debug(f"Prompt: {prompt}")

    def after_model(self, model_name: str, response: Any) -> None:
        """Called after Gemini returns a response."""
        self.logger.info(f"✅ [MODEL RESPONSE] Response received from {model_name}")

    def on_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> None:
        """Called when the model decides to use a tool."""
        self.logger.info(f"🛠️ [TOOL USE] Calling: {tool_name} | Args: {arguments}")

    def on_error(self, error: Exception) -> None:
        """Captures crashes."""
        self.logger.error(f"❌ [ERROR] {str(error)}", exc_info=True)