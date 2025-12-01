# src/config.py
import os
from dotenv import load_dotenv
from google.adk.models.google_llm import Gemini
from google.genai import types

# Load environment variables from a .env file if present
load_dotenv()

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

def get_model():
    """Returns the configured Gemini model instance."""
    # You can swap "gemini-2.5-flash" for "gemini-2.5-pro" for better reasoning
    return Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config)