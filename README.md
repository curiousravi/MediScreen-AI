🩺 MediScreen AI: The Intelligent Medical Intake System
Agents for Good Track | Kaggle Agents Intensive Capstone An AI-powered intake system that fights physician burnout and empowers patients.

📖 Overview
The Problem: Doctors currently spend up to 50% of their time on data entry and basic history gathering or they would start conversing with the patients directly to save the time and may loose to track important information to maintain the history. This leads to burnout, incorrect or less information storage, shorter, rushed patient visits where critical symptoms can be missed.

The Solution: MediScreen AI is a multi-agent system that acts as a "pre-visit" medical screener. It interviews patients before they enter the exam room, intelligently gathering symptoms, cross-referencing their medical history (via MCP), and generating a professional S.O.A.P.(Subjective, Objective, Assessment and Plan) note for the doctor.

Real-World Impact:

Efficiency: Given Doctor can visit patient for average 15 minute of booked time, MediScreen AI aves 5-7 minutes per patient visit.

Quality: Ensures comprehensive history taking without feeling rushed, Gives users ability to describe all their symptoms without any hesitation.

Safety: Provides a standardized, written brief for the doctor to review.

🏗️ Architecture
MediScreen AI uses a Hub-and-Spoke Multi-Agent Architecture powered by the Model Context Protocol (MCP).

Code snippet

graph TD
    User[Patient] <-->|Chat| Intake[Intake Coordinator Agent]
    Intake <-->|Delegates Interview| Symptom[Symptom Specialist Agent]
    Intake <-->|Fetches Data| History[History Archivist Agent]
    History <-->|MCP Protocol| MCPServer[Patient Data Server]
    Intake -->|Sends Raw Logs| Scribe[Clinical Scribe Agent]
    Scribe -->|Returns SOAP Note| Intake

The Agent Team
Intake Coordinator (MCP Host): The "Front Desk" Manages the session, routes tasks, and maintains context.

Symptom Specialist: A reasoning agent that conducts "drill-down" interviews based on specific complaints (e.g., dynamic questions for "headache" vs. "fever").

History Archivist: A tool-using agent that connects to our secure MCP Server to fetch patient records without hallucinating.

Clinical Scribe: A back-office agent that synthesizes raw chat logs into professional medical notes using Context Engineering.

📂 Project Structure
This project follows a production-grade modular design:

Plaintext

mediscreen-ai/
├── data/
│   └── mock_patients.json    # Simulated EMR database (No real PHI)
├── servers/
│   └── history_server.py     # MCP Server exposing patient data
├── src/
│   ├── agents/               # Individual Agent Logic
│   │   ├── intake.py
│   │   ├── symptom.py
│   │   └── scribe.py
│   ├── main.py               # Orchestrator & Entry Point
│   ├── config.py             # Model Configuration
│   └── prompts.py            # System Prompts (Context Engineering)
├── requirements.txt          # Dependencies
└── README.md                 # Documentation


🚀 Getting Started
Prerequisites
Python 3.10+

🌟 Features Enhancements 

1. Persistent Storage (SQLite)

2. Observability & Logging
- **Logs Location:** `logs/agent_trace_yyyy-mm-dd.log`,`logs\Patient_SOAP_NOTE_yyyy-mm-dd_hhmmss.txt`
- **What is logged:** - Agent start/stop events
  - Raw Model Inputs/Outputs
  - Tool execution (MCP calls)
  - Errors and Exceptions
  - Scribe Summary notes, post completion


A Google Cloud Project recommended with  Google AI Studio Key.

VS Code (Recommended for MCP development).

Installation
Clone the Repository

Bash

git clone https://github.com/yourusername/mediscreen-ai.git
cd mediscreen-ai
Install Dependencies

Bash

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
Configure Environment Create a .env file in the root directory:

Plaintext

GOOGLE_API_KEY=your_gemini_api_key_here
Usage
Run the System: This command launches both the Agent Client and the local MCP Server automatically.

Bash

python -m src.main

Demo Flow:

Login: Enter Patient ID PT-123 (Jane Doe) or PT-456 (John Smith).

Complaint: State a symptom (e.g., "I have a migraine").

Interview: The SymptomSpecialist will take over and ask follow-up questions.

Result: The system will generate a final S.O.A.P. Note in the terminal.


🔮 Future Roadmap: UI Integration
Currently, MediScreen AI operates via a CLI, but it is designed as an API-First Backend.

Proposed Integration: The IntakeCoordinator can be wrapped in a FastAPI websocket endpoint.

Frontend: A React Native mobile app or a hospital tablet interface (Streamlit) can connect to this endpoint.

Hospital System: The MCP Server (history_server.py) is designed to be swapped. In production, it would connect to a real FHIR-compliant database (e.g., Epic or Cerner) without changing the agent code.

🛡️ Ethics & Safety
Mock Data: This project uses entirely synthetic data (mock_patients.json). No real Patient Health Information (PHI) is used.

No Diagnosis: The system prompt explicitly forbids agents from offering medical diagnoses. It is strictly a documentation and intake tool.

