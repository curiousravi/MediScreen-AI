# Copyright 2025 MediScreen AI Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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