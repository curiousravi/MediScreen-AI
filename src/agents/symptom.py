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