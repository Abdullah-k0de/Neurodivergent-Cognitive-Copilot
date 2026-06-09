import time
from typing import List
from google import genai
from backend.memory_engine import MessageNode

def check_behavioral_state(history: List[MessageNode], current_content: str, last_timestamp: float) -> str:
    if not history:
        return "flow"
    time_delta = time.time() - last_timestamp
    char_count = len(current_content)
    if time_delta < 20 and char_count < 35:
        return "fragmented"
    return "flow"

def evaluate_confusion(client: genai.Client, active_goal: str, current_input: str) -> bool:
    if not client:
        return False
    prompt = f"""
    The user is returning to the task: "{active_goal}".
    User input: "{current_input}"
    Does this input show confusion, loss of context, or a request for a recap? (e.g. "what were we doing", "where did we leave off?", "huh?")
    Answer strictly with one word: TRUE or FALSE.
    """
    try:
        res = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt, 
            config={"temperature": 0.0, "max_output_tokens": 5}
        )
        return "TRUE" in res.text.strip().upper()
    except Exception:
        return False

def evaluate_dependency(client: genai.Client, active_goal: str, current_input: str, history: List[MessageNode]) -> bool:
    if not client:
        return True
        
    recent_context = "\n".join([f"{n.role.upper()}: {n.content}" for n in history[-3:]])
    prompt = f"""
    Main Goal: "{active_goal}"
    Recent Context:
    {recent_context}
    
    User Input: "{current_input}"
    Is the User Input a logical dependency, necessary component, or immediate debugging sub-task required to solve the Main Goal based on the Recent Context?
    Answer strictly with one word: TRUE or FALSE.
    """
    try:
        res = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt, 
            config={"temperature": 0.0, "max_output_tokens": 5}
        )
        return "TRUE" in res.text.strip().upper()
    except Exception:
        return True