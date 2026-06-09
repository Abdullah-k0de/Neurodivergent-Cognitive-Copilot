from uuid import uuid4
from google import genai
from backend.memory_engine import MemoryGraphManager, SessionState
from backend.classifier import check_behavioral_state, evaluate_dependency, evaluate_confusion

def handle_chat_routing(client: genai.Client, memory: MemoryGraphManager, state: SessionState, user_input: str) -> str:
    import time
    current_time = time.time()
    history = memory.get_main_branch_history(state.current_node_id) if state.current_node_id else []
    last_ts = history[-1].timestamp if history else current_time
    
    # 1. INITIALIZATION CHECK
    if not state.current_root_id:
        summary_prompt = f"""
        The user has provided their initial input: "{user_input}"
        Based on this, write a short, concise sentence stating their primary goal.
        Output ONLY the goal text, nothing else.
        """
        try:
            res = client.models.generate_content(model="gemini-2.5-flash", contents=summary_prompt)
            extracted_goal = res.text.strip()
        except Exception:
            extracted_goal = user_input
            
        state.active_primary_goal = extracted_goal
        node_id = memory.add_node("user", user_input, None, "INITIAL", 0)
        state.current_root_id = node_id
        memory.nodes_db[node_id].root_id = node_id
        
        init_prompt = f"""
        The user has established a new primary goal: "{extracted_goal}"
        Acknowledge the goal, and immediately provide a brief, structured breakdown of the first 2-3 execution steps to get started.
        """
        try:
            res = client.models.generate_content(model="gemini-2.5-flash", contents=init_prompt)
            ai_output = res.text
        except Exception as e:
            ai_output = f"⚠️ Gemini API Overloaded: Please try again in a few seconds."
            
        ai_node_id = memory.add_node("assistant", ai_output, node_id, node_id, 1)
        state.current_node_id = ai_node_id
        return ai_output

    # 2. TIME-BASED LAZY LOADING
    time_delta = current_time - last_ts
    if history and time_delta > 3600:
        state.re_entry_primed = True
        
    if state.re_entry_primed:
        is_confused = evaluate_confusion(client, state.active_primary_goal, user_input)
        if is_confused:
            scaffold_prompt = f"""
            The user has returned after a long break and lost context on the goal: "{state.active_primary_goal}".
            Recent history:
            {chr(10).join([f"{n.role.upper()}: {n.content}" for n in history[-5:]])}
            
            Provide a proactive scaffold: "Welcome back. We were working on [Goal]. We just finished [last step]. The next step is [next step]." Keep it concise.
            """
            try:
                res = client.models.generate_content(model="gemini-2.5-flash", contents=scaffold_prompt)
                ai_output = res.text
            except Exception as e:
                ai_output = f"⚠️ Gemini API Overloaded: Please try again in a few seconds."
            
            state.re_entry_primed = False
            
            # Save User Input then AI Scaffold sequentially to maintain graph integrity
            user_node_id = memory.add_node("user", user_input, state.current_node_id, state.current_root_id, history[-1].depth + 1)
            ai_node_id = memory.add_node("assistant", ai_output, user_node_id, state.current_root_id, history[-1].depth + 2)
            state.current_node_id = ai_node_id
            return ai_output
        else:
            state.re_entry_primed = False

    # 3. ROUTING & BEHAVIOR
    state.cognitive_state = check_behavioral_state(history, user_input, last_ts)
    is_sub_task = evaluate_dependency(client, state.active_primary_goal, user_input, history)
    
    parent_node = memory.nodes_db[state.current_node_id]
    next_depth = parent_node.depth + 1
    
    if is_sub_task:
        assigned_root = state.current_root_id
        state.in_tangent = False
    else:
        if parent_node.root_id.startswith("TANGENT_"):
            assigned_root = parent_node.root_id
        else:
            assigned_root = "TANGENT_" + str(uuid4())[:8]
        state.in_tangent = True
        
    user_node_id = memory.add_node("user", user_input, state.current_node_id, assigned_root, next_depth)
    state.current_node_id = user_node_id

    # 4. CONTEXT ASSEMBLY
    clean_history = memory.get_main_branch_history(user_node_id)
    
    if state.cognitive_state == "fragmented":
        sys_directive = "SYSTEM INSTRUCTION: User focus is fragmented. Respond in max 2 bullet points, use short sentences, and ask 1 simple micro-question.\n\n"
    else:
        sys_directive = "SYSTEM INSTRUCTION: Provide deep technical breakdown and comprehensive engineering architecture logic.\n\n"
        
    history_text = sys_directive + "\n".join([f"{n.role.upper()}: {n.content}" for n in clean_history])
    
    try:
        res = client.models.generate_content(model="gemini-2.5-flash", contents=history_text)
        ai_output = res.text
    except Exception as e:
        ai_output = f"⚠️ Gemini API Overloaded: Please try again in a few seconds."
    
    ai_node_id = memory.add_node("assistant", ai_output, user_node_id, assigned_root, next_depth + 1)
    state.current_node_id = ai_node_id
    
    # Notice: No state.in_tangent line here! It safely returns immediately.
    return ai_output

def handle_root_recovery(client: genai.Client, memory: MemoryGraphManager, state: SessionState) -> str:
    tangent_history = memory.get_main_branch_history(state.current_node_id)
    tangent_text = "\n".join([f"{n.role.upper()}: {n.content}" for n in tangent_history])
    
    synthesis_prompt = f"""
    The user is shifting back to their core task: "{state.active_primary_goal}".
    Analyze the recent context detour logs. Extract any technical parameters or configurations discovered that are explicitly helpful.
    Detour Logs: 
    {tangent_text}
    """
    
    try:
        summary_res = client.models.generate_content(model="gemini-2.5-flash", contents=synthesis_prompt)
        insights = summary_res.text
    except Exception:
        insights = "No specific insights extracted due to API limit."
    
    # Graph Traversal: Find the last node on the main branch
    curr_node = memory.nodes_db.get(state.current_node_id)
    attach_node = None
    
    while curr_node is not None:
        if not curr_node.root_id.startswith("TANGENT_"):
            attach_node = curr_node
            break
        curr_node = memory.nodes_db.get(curr_node.parent_id)
        
    attach_id = attach_node.node_id if attach_node else state.current_root_id
    attach_depth = attach_node.depth if attach_node else 0
    main_root_id = memory.nodes_db[attach_id].root_id
    
    state.current_node_id = attach_id
    state.current_root_id = main_root_id
    
    re_entry_prompt = f"""
    The user is returning to: "{state.active_primary_goal}".
    Extracted detour findings: {insights}.
    Acknowledge the return path, gracefully integrate what was discovered during the detour, and prompt for the next logical design step.
    """
    
    try:
        res = client.models.generate_content(model="gemini-2.5-flash", contents=re_entry_prompt)
        ai_output = res.text
    except Exception:
        ai_output = f"⚠️ Gemini API Overloaded: Returning to root goal."
    
    new_node_id = memory.add_node("assistant", ai_output, attach_id, main_root_id, attach_depth + 1)
    state.current_node_id = new_node_id
    state.cognitive_state = "flow"
    state.in_tangent = False
    
    return ai_output

def handle_goal_promotion(client: genai.Client, memory: MemoryGraphManager, state: SessionState) -> str:
    current_node = memory.nodes_db.get(state.current_node_id)
    if not current_node or not current_node.root_id.startswith("TANGENT_"):
        return "You are not currently in a tangent."
        
    tangent_root_id = current_node.root_id
    history = memory.get_main_branch_history(state.current_node_id)
    tangent_nodes = [n for n in history if n.root_id == tangent_root_id]
    tangent_text = "\n".join([f"{n.role.upper()}: {n.content}" for n in tangent_nodes])
    
    prompt = f"""
    The user has decided to promote their recent conversational tangent into their new primary goal.
    Tangent Logs:
    {tangent_text}
    
    Based on these logs, write a short, concise sentence stating the new primary goal. 
    Output ONLY the goal text, nothing else.
    """
    try:
        res = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        new_goal = res.text.strip()
    except Exception:
        first_user_node = next((n for n in tangent_nodes if n.role == "user"), None)
        new_goal = first_user_node.content if first_user_node else "New Tangent Goal"
        
    state.active_primary_goal = new_goal
    state.current_root_id = tangent_root_id
    state.in_tangent = False
    
    ai_output = f"⭐ **Goal Promoted!**\nOur new primary focus is now: *{new_goal}*"
    new_node_id = memory.add_node("assistant", ai_output, state.current_node_id, tangent_root_id, current_node.depth + 1)
    state.current_node_id = new_node_id
    
    return ai_output