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



# src/utils.py, similar to helper functions
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.genai import types

async def get_or_create_session(
    session_service: InMemorySessionService, 
    app_name: str, 
    user_id: str, 
    session_id: str
):
    """
    Safely retrieves an existing session or creates a new one if it doesn't exist.
    """
    #print(f"[SYSTEM] Initializing Session: {session_id}...")
    try:
        # Try to create a new session
        # Note: explicit app_name is required by newer ADK versions
        await session_service.create_session(
            session_id=session_id,
            user_id=user_id,
            app_name=app_name 
        )
        #print("[SYSTEM] Session Created Successfully.")
    except Exception as e:
        # If creation fails (likely because it exists), we just proceed.
        # We don't strictly need to 'get' it for the Runner to work, 
        # Silently ignore as long as it exists in the service.
        pass
        #print(f"[SYSTEM] Session already exists (or error ignored): {e}")

async def run_agent_turn(
    runner: Runner,
    user_input: str,
    user_id: str,
    session_id: str
) -> str:
    """
    Handles the nitty-gritty of converting text to ADK content, 
    streaming the response, and returning the final text.
    """
    # 1. Convert string to strictly typed Content object
    user_msg = types.Content(role="user", parts=[types.Part(text=user_input)])

    final_text_response = ""

    # 2. Stream the response (Handling the async generator)
    try:
        async for event in runner.run_async(
            new_message=user_msg,
            user_id=user_id,
            session_id=session_id
        ):
            # Capture the text from the event
            # (In complex agents, you might get Thought Traces here too, but we filter for text)
            if event.content and event.content.parts:
                part_text = event.content.parts[0].text
                if part_text and part_text != "None":
                    final_text_response = part_text
                    # Optional: Print streaming chunks here if you want a "typing" effect
    except Exception as e:
        #print(f"[ERROR] Agent Execution Failed: {e}")
        return f"[ I encountered an error processing your request System Error: {str(e)} ]" 

    return final_text_response