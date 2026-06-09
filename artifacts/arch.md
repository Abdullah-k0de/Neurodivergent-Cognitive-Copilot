# The Cognitive Copilot: An OS for Neurodivergent Thought

## 1. The Core Philosophy

Current AI chatbots treat human thought as a single, chronological script (a flat `[message_1, message_2]` array). If a user gets distracted, the AI's context window gets polluted, and the original goal is lost.

**The Cognitive Copilot** abandons this flat array in favor of a **Directed Acyclic Graph (DAG)**. It treats human cognition like a computer operating system: managing processes, handling interrupts, isolating child threads (tangents), and managing context-switching. This fundamentally shifts the AI from a conversational wrapper to a **State-Aware Cognitive Engine** specifically tailored to support executive function—making it a game-changer for neurodivergent users, particularly those with ADHD.

---

## 2. Technical Architecture Overview

* **Backend:** Python `FastAPI` providing asynchronous, stateful REST endpoints (`/chat`, `/recover-root`, `/state`, `/visualize`).
* **Memory Engine:** A custom-built DAG (Directed Acyclic Graph) memory structure. Nodes contain metadata (role, content, timestamp, parent pointer, root anchor pointer).
* **Intelligence:** Google's `gemini-2.5-flash` model, utilized for both conversational generation and behind-the-scenes behavioral classification.
* **Frontend:** `Streamlit`, providing a real-time visualization of the user's cognitive state and UI controls.
* **Visualization:** `PyVis` Network graphs to compile interactive HTML maps of the user's thought process.

---

## 3. Scenario Breakdown: What Happens When...

### Scenario A: Goal Initialization (The Root Anchor)

**User Action:** The user types their first prompt (e.g., *"I need to write a Python script to scrape a weather site."*)

**Technical Execution:**

1. The `router.py` initialization block detects `state.current_root_id` is empty.
2. It creates a new `MessageNode` with the attribute `root_id = "INITIAL"`. This node's unique ID becomes the permanent **Anchor Root**.
3. The backend queries the LLM in the background to immediately break down the prompt into 2-3 structured execution steps.
4. The goal is locked into the `SessionState`.

**Neurodivergent Value (Preventing Scope Creep):**
ADHD brains often struggle with "starting" (task initiation) and maintaining the big picture. By explicitly forcing the system to anchor to a primary goal and immediately mapping out steps, the Copilot provides an unmoving "North Star." No matter how far the user strays, the system remembers the exact task they sat down to do.

> [!TIP]
> **Key Metric (The Anchor vs. The Float):** In the current architecture, `active_primary_goal` acts as a **Fixed Anchor**—it remains immutable unless explicitly reset. If the goal were "floating" (changing based on the tangent), the user would risk losing their original objective entirely when going down a rabbit hole. By keeping it fixed, the system guarantees a safe return path. (However, a "Goal Migration" algorithm *could* be implemented if a tangent organically evolves into the new primary task).

---

### Scenario B: Behavioral Classification (Adaptive Cadence)

**User Action:** The user gets frustrated or overwhelmed and types several short, rapid-fire messages (e.g., *"wait"*, *"errors?"*, *"why isn't it working"*).

**Technical Execution:**

1. The `classifier.py` calculates the `time_delta` since the last message and the `char_count` of the new message.
2. If the user types rapidly (under 20 seconds) with short bursts (under 35 characters), the `check_behavioral_state` function flips the `state.cognitive_state` from `"flow"` to `"fragmented"`.
3. The `router.py` intercepts this state change and dynamically prepends a hidden system directive to the LLM prompt:
   `"SYSTEM INSTRUCTION: User focus is fragmented. Respond in max 2 bullet points, use short sentences, and ask 1 simple micro-question."`

**Neurodivergent Value (De-escalating Overwhelm):**
When executive dysfunction hits, reading a massive wall of AI-generated text induces paralysis. The Copilot detects this panic state via typing kinematics and instantly dials down its verbosity. It feeds the user bite-sized, highly actionable micro-steps, acting as a calming, regulating presence.

---

### Scenario C: The Tangent Detour (Branch Isolation)

**User Action:** While working on the weather scraper, the user gets distracted and asks, *"What's the best torque ratio for a TotGuard e-bike?"*

**Technical Execution:**

1. Before routing the chat, the system runs `evaluate_dependency`—a background LLM check. It feeds the following hidden prompt to the Gemini API:
   ```text
   Main Goal: "{active_goal}"
   Recent Context: {recent_context}
   User Input: "{current_input}"
   Is the User Input a logical dependency, necessary component, or immediate debugging sub-task required to solve the Main Goal based on the Recent Context? Answer strictly with one word: TRUE or FALSE.
   ```
2. The LLM evaluates the e-bike question against the weather scraper context and returns `FALSE`.
3. `router.py` detects this and assigns a new root pointer (`assigned_root = "TANGENT_xxxx"`).
4. The new nodes are saved to the DAG, pointing to each other, but structurally isolated from the main "blue" branch. The `state.in_tangent` flag is set to `True`.

**Neurodivergent Value (Healthy Rabbit Holes):**
Standard AI chatbots get irreparably confused when you change the subject, forgetting the original context. The Copilot *embraces* the ADHD tendency to follow dopamine trails. It lets the user explore the tangent safely, placing it in a sandbox (a side-branch in the DAG) so that the core working memory remains perfectly pristine.

---

### Scenario D: Context Teleportation (Recover Goal)

**User Action:** The user realizes they are on a tangent. The UI displays a **"↩️ Recover Goal"** button. The user clicks it.

**Technical Execution:**

1. The `/recover-root` endpoint triggers `handle_root_recovery`.
2. The engine extracts all logs from the active tangent branch and runs a synthesis prompt to extract any technically useful insights.
3. **Graph Traversal:** The engine walks backward up the DAG's `parent_id` pointers until it hits the last node that belonged to the main branch.
4. It generates a seamless re-entry message, appends it to that exact main-branch node, and resets the user's active pointer back to the main goal.

**Neurodivergent Value (The One-Click Parachute):**
The hardest part of ADHD is returning to the task after a distraction. The Copilot provides a literal parachute. With one click, the user is teleported back to the exact moment before they got distracted, with the AI gracefully summarizing the detour and pointing them to the next step. No manual scrolling or re-explaining is required.

---

### Scenario E: Time-Based Lazy Loading (Scaffolded Re-entry)

**User Action:** The user leaves the tab open, goes to lunch, gets distracted by a meeting, and returns 2 hours later. They type, *"huh?"* or *"what were we doing?"*

**Technical Execution:**

1. `router.py` checks the `time_delta` against the last node's timestamp. If it exceeds 3600 seconds (1 hour), it sets `state.re_entry_primed = True`.
2. The `evaluate_confusion` background function analyzes the user's new input.
3. If confusion is detected, the AI generates a proactive scaffold, bypassing the standard response generation:
   *“Welcome back. We were working on [Goal]. We just finished [last step]. The next step is [next step].”*
4. This scaffold is injected seamlessly into the DAG.

**Neurodivergent Value (Curing Time Blindness & Amnesia):**
"Time blindness" and losing one's train of thought after a break are massive hurdles for neurodivergent workers. The Copilot anticipates this context-loss. Instead of forcing the user to re-read the chat history to figure out where they left off, the AI proactively provides a "previously on..." recap, lowering the cognitive barrier to resuming work to absolute zero.

---

## 4. Conclusion

The Cognitive Copilot is not just an AI interface; it is an **externalized executive function engine**. By mirroring the structure of human thought through DAG node mapping—and dynamically adapting to the user's behavioral state—it transforms AI from a passive tool into an active, regulating partner designed explicitly for neurodivergent success.
