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


# src/agents/scribe.py
from google.adk.agents import Agent
from src.config import get_model
from src.prompts import SCRIBE_SYS

class ClinicalScribe:
    def __init__(self):
        self.agent = Agent(
            name="ClinicalScribe",
            model=get_model(),
            instruction=SCRIBE_SYS
        )

    async def generate_note(self, chat_log, patient_history):
        """
        Synthesizes the final note.
        Note: We combine inputs into a single prompt string for the agent.
        """
        combined_input = f"""
        TASK: Create a SOAP(Subjective, Objective, Assessment and Plan) note.
        
        [PATIENT HISTORY]
        {patient_history}
        
        [INTERVIEW LOG]
        {chat_log}
        """
                
        response = self.agent.run(combined_input)
        
        # Check if response implies .text or if it returns the string directly
        # If the ADK returns a string, just return response.
        # If it returns an object, return response.text
        # Safe bet:
        try:
            return response.text
        except AttributeError:
            return str(response)