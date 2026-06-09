import os
from fastapi import FastAPI, HTTPException
from google import genai
from dotenv import load_dotenv

from backend.memory_engine import MemoryGraphManager, SessionState
from backend.router import handle_chat_routing, handle_root_recovery, handle_goal_promotion

load_dotenv() 

app = FastAPI(title="Cognitive Copilot Engine")

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

memory = MemoryGraphManager()
state = SessionState(active_primary_goal="", current_root_id="")

@app.get("/state")
async def get_state():
    return state

@app.get("/visualize")
async def visualize():
    memory.generate_graph_html(state.current_root_id, filename="dag_visual.html")
    return {"status": "success", "file": "dag_visual.html"}

@app.post("/reset")
async def reset_engine():
    global memory, state
    memory = MemoryGraphManager()
    state = SessionState(active_primary_goal="", current_root_id="")
    return {"status": "system reset complete"}

@app.post("/chat")
async def chat_endpoint(user_input: str):
    if not client:
        raise HTTPException(status_code=500, detail="Gemini client uninitialized.")
    try:
        response_text = handle_chat_routing(client, memory, state, user_input)
        return {"response": response_text, "state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recover-root")
async def recover_endpoint():
    if not client:
        raise HTTPException(status_code=500, detail="Gemini client uninitialized.")
    if not state.current_root_id:
        raise HTTPException(status_code=400, detail="No active root context.")
    try:
        response_text = handle_root_recovery(client, memory, state)
        return {"response": response_text, "state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/promote-goal")
async def promote_endpoint():
    if not client:
        raise HTTPException(status_code=500, detail="Gemini client uninitialized.")
    try:
        response_text = handle_goal_promotion(client, memory, state)
        return {"response": response_text, "state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))