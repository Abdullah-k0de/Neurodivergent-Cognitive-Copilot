import streamlit as st
import requests

st.set_page_config(page_title="Cognitive Copilot Workspace", layout="centered")
st.title("🧠 Cognitive Copilot Workspace")

URL = "http://127.0.0.1:8000"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "backend_state" not in st.session_state:
    st.session_state.backend_state = {"active_primary_goal": "Uninitialized", "cognitive_state": "flow", "current_node_id": None, "current_root_id": ""}

try:
    res = requests.get(f"{URL}/state")
    if res.status_code == 200:
        st.session_state.backend_state = res.json()
except Exception:
    pass

with st.sidebar:
    st.header("Graph Structural Metrics")
    st.metric(label="Active Goal Anchor", value=st.session_state.backend_state.get("active_primary_goal") or "None")
    
    cog = st.session_state.backend_state.get("cognitive_state", "flow").upper()
    if cog == "FRAGMENTED":
        st.error("⚠️ FRAGMENTED ATTENTION DETECTED")
    else:
        st.success("⚡ STABLE COGNITIVE FLOW")
        
    st.subheader("System Control Operations")
    if st.button("👁️ Compile Interactive DAG Map"):
        viz_res = requests.get(f"{URL}/visualize")
        if viz_res.status_code == 200:
            st.sidebar.success("Map compiled! Check the project root directory for 'dag_visual.html'.")
            
    if st.button("🗑️ Clear Context Graph"):
        requests.post(f"{URL}/reset")
        st.session_state.chat_history = []
        st.rerun()

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- UI VISIBILITY FIX ---
in_tangent = st.session_state.backend_state.get("in_tangent", False)

if in_tangent:
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"↩️ Recover Goal: {st.session_state.backend_state['active_primary_goal']}"):
            with st.spinner("Processing path re-entry synthesis..."):
                rec_res = requests.post(f"{URL}/recover-root")
                if rec_res.status_code == 200:
                    data = rec_res.json()
                    st.session_state.backend_state = data["state"]
                    st.session_state.chat_history.append({"role": "assistant", "content": data["response"]})
                    st.rerun()
    with col2:
        if st.button("⭐ Promote to Main Goal"):
            with st.spinner("Promoting tangent to main goal..."):
                prom_res = requests.post(f"{URL}/promote-goal")
                if prom_res.status_code == 200:
                    data = prom_res.json()
                    st.session_state.backend_state = data["state"]
                    st.session_state.chat_history.append({"role": "assistant", "content": data["response"]})
                    st.rerun()

if user_input := st.chat_input("Enter message..."):
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
        
    with st.spinner("Processing pipeline execution steps..."):
        chat_res = requests.post(f"{URL}/chat", params={"user_input": user_input})
        if chat_res.status_code == 200:
            data = chat_res.json()
            st.session_state.backend_state = data["state"]
            st.session_state.chat_history.append({"role": "assistant", "content": data["response"]})
            st.rerun()