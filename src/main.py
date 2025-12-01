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


import asyncio
import os
import logging
import sys
import datetime

# --- 1. AGGRESSIVE LOGGING SUPPRESSION (Must be at the top) ---
# Redirect standard logs to null or file to keep console clean
logging.basicConfig(level=logging.CRITICAL)  # Only show critical errors
logger = logging.getLogger("mediscreen_main")
logger.setLevel(logging.INFO) # We will use this one for our file logs

# Silence specific libraries that are chatty
for lib in ["google.adk", "absl", "mcp", "urllib3", "asyncio"]:
    logging.getLogger(lib).setLevel(logging.CRITICAL)

# Redirect absl logging (used by Google libs) to avoid "App name mismatch"
try:
    import absl.logging
    absl.logging.set_verbosity(absl.logging.FATAL)
except ImportError:
    pass
# -------------------------------------------------------------

from dotenv import load_dotenv

# ADK & GenAI
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from sqlalchemy import create_engine
import uuid

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Local Modules
from src.agents.intake import IntakeCoordinator
from src.agents.symptom import SymptomSpecialist
from src.agents.scribe import ClinicalScribe
from src.utils import get_or_create_session, run_agent_turn
from src.plugins import FileLoggingPlugin

load_dotenv()

async def run_mediscreen():
    # Setup our file tracer (Logs go here, not to screen)
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file_path = f"logs/agent_trace_{today_str}.log"
    tracer = FileLoggingPlugin(log_file_path=log_file_path)
    #Old: tracer = FileLoggingPlugin(log_file_path="logs/agent_trace.log")
    
    # We use the tracer's internal logger for system messages now
    system_log = tracer.logger 
    system_log.info("--- SYSTEM STARTUP ---")

    # DB Setup
    db_url = "sqlite:///mediscreen.db"
    session_service = DatabaseSessionService(db_url=db_url)
    system_log.info(f"--- Logging and Database Connection Initialized ---")

    # MCP Setup
    server_params = StdioServerParameters(
        command="python",
        args=["servers/history_server.py"],
        env=os.environ
    )

    # We redirect stderr to devnull temporarily to hide MCP startup logs if needed
    # But usually, the logging.CRITICAL above catches most python-based logs.
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            async def fetch_history_tool(patient_id: str):
                tracer.on_tool_call("get_patient_history", {"patient_id": patient_id})
                result = await session.call_tool("get_patient_history", arguments={"patient_id": patient_id})
                return result.content[0].text

            # Initialize Agents
            intake_wrapper = IntakeCoordinator(tools=[fetch_history_tool])
            symptom_wrapper = SymptomSpecialist()
            scribe_wrapper = ClinicalScribe()
            
            app_name = "mediscreen_ai"

            # Initialize Runners
            intake_runner = Runner(agent=intake_wrapper.agent, session_service=session_service, app_name=app_name)
            symptom_runner = Runner(agent=symptom_wrapper.agent, session_service=session_service, app_name=app_name)
            scribe_runner = Runner(agent=scribe_wrapper.agent, session_service=session_service, app_name=app_name)

            # Session Setup
            USER_ID = "patient_cli_user" 
            SESSION_ID = str(uuid.uuid4())

            CURRENT_PATIENT_ID = USER_ID # Initialize with the generic CLI user ID
            
            # Log this to file, don't print
            system_log.info(f"Initializing Session: {SESSION_ID}")
            await get_or_create_session(session_service, app_name, USER_ID, SESSION_ID)

            # --- MAIN LOOP SETUP ---
            current_runner = intake_runner
            current_agent_name = "IntakeCoordinator"
            full_conversation_log = []

            print("\n" + "="*50)
            print("🏥  MEDISCREEN AI  |  System Online")
            print("="*50 + "\n")

            # --- 2. WARM START (Auto-Introduction) ---
            # We send a hidden instruction to the agent to make it speak first.
            start_instruction = "The user has connected. Introduce yourself and ask for their Patient ID."
            tracer.before_agent(current_agent_name, "SYSTEM_TRIGGER: " + start_instruction)
            
            intro_response = await run_agent_turn(
                runner=current_runner,
                user_input=start_instruction,
                user_id=USER_ID,
                session_id=SESSION_ID
            )
            
            print(f"{current_agent_name}: {intro_response}\n")
            full_conversation_log.append(f"{current_agent_name}: {intro_response}")

            # --- 3. INTERACTIVE LOOP ---
            while True:
                try:
                    user_input = input("Patient: ")
                except EOFError:
                    break

                # --- 4. EMPTY INPUT HANDLING ---
                if not user_input.strip():
                    print(f"\n{current_agent_name}: I didn't catch that. Please type your response.\n")
                    continue
                
                if user_input.lower() in ["quit", "exit"]:
                    print("\nClosing Session. Goodbye!")
                    break
                
                full_conversation_log.append(f"Patient: {user_input}")
                tracer.before_agent(current_agent_name, user_input)

                agent_response = await run_agent_turn(
                    runner=current_runner,
                    user_input=user_input,
                    user_id=USER_ID,
                    session_id=SESSION_ID
                )
                
                tracer.after_model(current_agent_name, agent_response)

                # Only print if we actually got text back (handles silent tool use)
                if agent_response and agent_response.strip():
                    print(f"\n{current_agent_name}: {agent_response}\n")
                    full_conversation_log.append(f"{current_agent_name}: {agent_response}")
                else:
                    # If response is empty (rare, but happens on tool use sometimes), don't print a blank line
                    pass 

                # --- ROUTING LOGIC ---
                if current_agent_name == "IntakeCoordinator":
                    # Check if the IntakeCoordinator has responded with the patient's name
                    if "thank you," in agent_response.lower() and "i see your file" in agent_response.lower():
                        # Heuristic: The model's response should be immediately after the tool call.
                        # We try to extract the ID from the user's *last* input.
                        last_user_input = full_conversation_log[-2].split("Patient: ")[-1]
                        
                        # Use regex or a simple split to find the ID (e.g., PT-1004)
                        import re
                        match = re.search(r'(PT-\d+)', last_user_input, re.IGNORECASE)
                        if match:
                            # --- UPDATE THE DYNAMIC ID ---
                            #CURRENT_PATIENT_ID = match.group(0).upper()
                            CURRENT_PATIENT_ID = match.group(0).upper()
                            system_log.info(f"Patient ID successfully extracted and set to: {CURRENT_PATIENT_ID}")
                    
                    # Check for explicit handoff text
                    if "specialist" in agent_response.lower() and "connect you" in agent_response.lower():
                        system_log.info("Handing off to SymptomSpecialist")
                        
                        current_runner = symptom_runner
                        current_agent_name = "SymptomSpecialist"
                        
                        # Warm Handoff
                        # Ensure we use the most recently recognized ID for context
                        handoff_context = f"Patient ID: {CURRENT_PATIENT_ID} is on the line. Complaint: {user_input}."
                        
                        # We run this hidden turn to get the specialist to greet the user
                        greeting = await run_agent_turn(current_runner, handoff_context, USER_ID, SESSION_ID)
                        print(f"\n{current_agent_name}: {greeting}\n")
                        full_conversation_log.append(f"{current_agent_name}: {greeting}")

                elif current_agent_name == "SymptomSpecialist":
                    if "SUMMARY_COMPLETE" in agent_response:
                        system_log.info("Interview Complete. Generating Note for Doctor to review.")
                        #print("\n[Generating Clinical Note...]\n")
                        
                        scribe_input = f"GENERATE SOAP NOTE.\n[LOGS]: {' '.join(full_conversation_log)}"
                        tracer.before_agent("ClinicalScribe", scribe_input)
                        
                        final_note = await run_agent_turn(scribe_runner, scribe_input, USER_ID, SESSION_ID)
                        
                        tracer.after_model("ClinicalScribe", final_note)
                        
                        # --- SAVE TO FILE ---
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"logs/{CURRENT_PATIENT_ID}_SOAP_Note_{timestamp}.txt"
                        
                        # Ensure logs dir exists (it should, but safety first)
                        os.makedirs("logs", exist_ok=True)
                        
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(final_note)
                        # Print Clinical notes to console within separators, For Demo purposes
                        print("="*50)
                        print(final_note)
                        print("="*50)
                        #print(f"\n✅ Clinical Note saved to: {filename}")
                        #print("System shutting down. Goodbye!")
                        break

'''                elif current_agent_name == "SymptomSpecialist":
                    if "SUMMARY_COMPLETE" in agent_response:
                        system_log.info("Interview Complete. Generating Note.")
                        print("\n[Generating Clinical Note...]\n")
                        
                        scribe_input = f"GENERATE SOAP NOTE.\n[LOGS]: {' '.join(full_conversation_log)}"
                        tracer.before_agent("ClinicalScribe", scribe_input)
                        
                        final_note = await run_agent_turn(scribe_runner, scribe_input, USER_ID, SESSION_ID)
                        
                        tracer.after_model("ClinicalScribe", final_note)
                        print("="*50 + "\n" + final_note + "\n" + "="*50)
                        break
'''
if __name__ == "__main__":
    try:
        asyncio.run(run_mediscreen())
    except KeyboardInterrupt:
        print("\nSystem forced shutdown.")