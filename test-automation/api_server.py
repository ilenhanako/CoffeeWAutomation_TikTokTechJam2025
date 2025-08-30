import uvicorn
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from typing import List, Optional

from main import run_automation

app = FastAPI()
# python -m uvicorn api_server:app --host 0.0.0.0 --port 8000


# ----- Request/Response Schemas -----
class Step(BaseModel):
    step_id: str
    description: str
    action_type: str
    expected_state: Optional[str] = None
    query_for_qwen: Optional[str] = None

class Scenario(BaseModel):
    scenario_id: str
    scenario_title: str
    steps: List[Step]

class RunRequest(BaseModel):
    business_goal: str
    scenarios: List[Scenario]

# ----- Endpoints -----
@app.post("/run")
async def run_scenarios(req: RunRequest):

    run_automation(req.business_goal, req.scenarios)
    return {"status": "started", "business_goal": req.business_goal}


@app.websocket("/logs")
async def stream_logs(ws: WebSocket):
    """
    Streamlit subscribes here to get real-time logs and screenshots.
    """
    await ws.accept()
    # Attach this websocket to logger stream
    from utils.logging import register_ws
    register_ws(ws)
    try:
        while True:
            msg = await ws.receive_text()
            await ws.send_text(f"echo: {msg}")  # keep alive
    except Exception:
        pass
