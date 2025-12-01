import json
import os
from mcp.server.fastmcp import FastMCP
import logging


# This ensures the MCP server process doesn't print INFO logs to stderr
logging.basicConfig(level=logging.CRITICAL)
# ----------------------------------

# Initialize the MCP Server
mcp = FastMCP("HistoryArchivist")


# Load data (In production, this would connect to a SQL DB)
DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/mock_patients.json')

def load_db():
    with open(DATA_PATH, 'r') as f:
        return json.load(f)

@mcp.tool()
def get_patient_history(patient_id: str) -> str:
    """
    Retrieves the full medical history for a given Patient ID.
    Args:
        patient_id: The ID of the patient (e.g., 'PT-123')
    Returns:
        JSON string of patient history or error message.
    """
    db = load_db()
    patient = db.get(patient_id)
    
    if patient:
        return json.dumps(patient, indent=2)
    else:
        return f"Error: Patient ID '{patient_id}' not found."

@mcp.resource("hospital://protocols/intake")
def get_intake_protocol() -> str:
    """Returns the standard operating procedure for new patient intake."""
    return "1. Verify ID. 2. Get Chief Complaint. 3. Check Vitals."

if __name__ == "__main__":
    mcp.run()