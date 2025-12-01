# 🩺 MediScreen AI: The Intelligent Medical Intake System

**Agents for Good Track | Kaggle Agents Intensive Capstone**

An AI-powered intake system that fights physician burnout and empowers patients.

---

## ⚠️ IMPORTANT DISCLAIMERS

### Medical Disclaimer
**THIS SOFTWARE IS FOR RESEARCH AND EDUCATIONAL PURPOSES ONLY.**

- **NOT for clinical use**: MediScreen AI is not intended for use in clinical diagnosis, treatment, or medical decision-making.
- **NOT a medical device**: This software is not FDA-approved or certified as a medical device.
- **NOT a substitute for professional care**: Always consult qualified healthcare professionals for medical advice, diagnosis, or treatment.
- **No doctor-patient relationship**: Use of this software does not create a doctor-patient relationship.
- **Emergency situations**: In case of medical emergency, call emergency services immediately (911 in US).

### Data Privacy Notice
- This demonstration uses entirely **synthetic patient data**
- No real Patient Health Information (PHI) is collected or stored
- In production deployment, proper HIPAA compliance and security measures must be implemented

---

## 📖 Overview

### The Problem
Doctors currently spend up to 50% of their time on data entry and basic history gathering. When they try to save time by conversing directly with patients, they may lose track of important information needed to maintain proper medical histories. This leads to:
- Physician burnout
- Incomplete or incorrect information storage
- Shorter, rushed patient visits
- Critical symptoms being missed

### The Solution
MediScreen AI is a multi-agent system that acts as a "pre-visit" medical screener. It interviews patients before they enter the exam room, intelligently gathering symptoms, cross-referencing their medical history (via MCP), and generating a professional S.O.A.P. (Subjective, Objective, Assessment and Plan) note for the doctor.

### Real-World Impact

**Efficiency:** Saves 5-7 minutes per patient visit (out of typical 15-minute appointments)

**Quality:** Ensures comprehensive history taking without feeling rushed. Gives patients the ability to describe all their symptoms without hesitation.

**Safety:** Provides a standardized, written brief for the doctor to review.

---

## 🗺️ Architecture

MediScreen AI uses a Hub-and-Spoke Multi-Agent Architecture powered by the Model Context Protocol (MCP).

![MediScreen AI Architecture](assets/architecture.png)


```mermaid
graph TD
    User[Patient] <-->|Chat| Intake[Intake Coordinator Agent]
    Intake <-->|Delegates Interview| Symptom[Symptom Specialist Agent]
    Intake <-->|Fetches Data| History[History Archivist Agent]
    History <-->|MCP Protocol| MCPServer[Patient Data Server]
    Intake -->|Sends Raw Logs| Scribe[Clinical Scribe Agent]
    Scribe -->|Returns SOAP Note| Doctor to review
```

### The Agent Team

**Intake Coordinator (MCP Host):** The "Front Desk" - Manages the session, routes tasks, and maintains context.

**Symptom Specialist:** A reasoning agent that conducts "drill-down" interviews based on specific complaints (e.g., dynamic questions for "headache" vs. "fever").

**History Archivist:** A tool-using agent that connects to our secure MCP Server to fetch patient records without hallucinating.

**Clinical Scribe:** A back-office agent that synthesizes raw chat logs into professional medical notes using Context Engineering.

---

## 📂 Project Structure

This project follows a production-grade modular design:

```
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
├── LICENSE                   # Apache 2.0 License
└── README.md                 # Documentation
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- A Google Cloud Project with Google AI Studio Key (recommended)
- VS Code (recommended for MCP development)

### Installation

**1. Clone the Repository**

```bash
git clone https://github.com/curiousravi/MediScreen-AI.git
cd mediscreen-ai
```

**2. Install Dependencies**

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**3. Configure Environment**

Create a `.env` file in the root directory:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Usage

**Run the System:**

```bash
python -m src.main
```

This command launches both the Agent Client and the local MCP Server automatically.

**Demo Flow:**

1. **Login:** Enter Patient ID `PT-123` (Jane Doe) or `PT-456` (John Smith)
2. **Complaint:** State a symptom (e.g., "I have a migraine")
3. **Interview:** The SymptomSpecialist will take over and ask follow-up questions
4. **Result:** The system will generate a final S.O.A.P. Note in the terminal

---

## 🌟 Features & Enhancements

### 1. Persistent Storage (SQLite)
Patient data and session information stored locally for continuity.

### 2. Observability & Logging

**Logs Location:** 
- `logs/agent_trace_yyyy-mm-dd.log`
- `logs/Patient_SOAP_NOTE_yyyy-mm-dd_hhmmss.txt`

**What is logged:**
- Agent start/stop events
- Raw Model Inputs/Outputs
- Tool execution (MCP calls)
- Errors and Exceptions
- Scribe Summary notes, post completion

---

## 🔮 Future Roadmap: UI Integration

Currently, MediScreen AI operates via a CLI, but it is designed as an **API-First Backend**.

**Proposed Integration:**
- The IntakeCoordinator can be wrapped in a FastAPI websocket endpoint
- **Frontend:** A React Native mobile app or hospital tablet interface (Streamlit) can connect to this endpoint
- **Hospital System:** The MCP Server (`history_server.py`) is designed to be swapped. In production, it would connect to a real FHIR-compliant database (e.g., Epic or Cerner) without changing the agent code.

---

## 🛡️ Ethics & Safety

### Mock Data Only
This project uses entirely **synthetic data** (`mock_patients.json`). No real Patient Health Information (PHI) is used or stored.

### No Diagnosis
The system prompt explicitly forbids agents from offering medical diagnoses. It is strictly a **documentation and intake tool**.

### Intended Use
- **Educational purposes**: Learning about multi-agent AI systems
- **Research purposes**: Exploring healthcare AI applications
- **Demonstration purposes**: Showcasing MCP integration
- **NOT for clinical use**: Must not be used for actual patient care

### Production Deployment Considerations
If adapting this project for real-world use, you must:
- Implement proper HIPAA compliance measures
- Obtain necessary medical device certifications if required
- Conduct clinical validation studies
- Implement robust security and encryption
- Ensure proper consent and privacy controls
- Consult with healthcare legal and compliance experts

---

## 📄 License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for complete details.

### Key Points:
- ✅ Free to use, modify, and distribute
- ✅ Commercial use permitted
- ✅ Patent grant included
- ⚠️ **NO WARRANTY** - Software provided "AS IS"
- ⚠️ **NO LIABILITY** - Use at your own risk
- 📋 Must include license and copyright notice in distributions

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Contact

**Project Repository:** [https://github.com/curiousravi/MediScreen-AI](https://github.com/curiousravi/MediScreen-AI)

**Questions or Issues:** Please open an issue on GitHub

---

## 🙏 Acknowledgments

- Built for the **Kaggle Agents Intensive Capstone** (Agents for Good Track)
- Powered by **Google Gemini** and the **Model Context Protocol (MCP)**
- Inspired by the need to reduce physician burnout and improve patient care

---

**Remember:** This is a demonstration project for educational purposes. Always consult qualified healthcare professionals for medical advice.