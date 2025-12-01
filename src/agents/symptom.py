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


# src/agents/symptom.py
from google.adk.agents import Agent
from src.config import get_model
from src.prompts import SYMPTOM_SPECIALIST_SYS

class SymptomSpecialist:
    def __init__(self):
        self.agent = Agent(
            name="SymptomSpecialist",
            model=get_model(),
            instruction=SYMPTOM_SPECIALIST_SYS
            # In the future, you can add a tool here like 'get_medical_guidelines'
        )

    async def run(self, user_input):
        response = self.agent.run(user_input)
        return response