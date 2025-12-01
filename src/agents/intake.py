# src/agents/intake.py
from google.adk.agents import Agent
from src.config import get_model
from src.prompts import INTAKE_COORDINATOR_SYS

class IntakeCoordinator:
    def __init__(self, tools=None):
        self.agent = Agent(
            name="IntakeCoordinator",
            model=get_model(),
            instruction=INTAKE_COORDINATOR_SYS,
            tools=tools if tools else []  # Pass the History Tool here
        )

    