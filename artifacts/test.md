# 🧠 ADHD Cognitive Copilot: System Testing Guide

This guide outlines the scenarios and steps required to test the core features of the ADHD Cognitive Copilot, including goal anchoring, cognitive load evaluation, fragmented attention control, tangent isolation, and recovery.

---

## 🧪 Phase 1 & 2: Interactive Session Scenarios

### 📍 Test 1: The Root Anchor Check
Verify that the system successfully initializes and locks a primary goal anchor.

* **Interaction Type:** Goal Initialization
* **User Input:** 
  > *"I need to write a Python script to scrape data from a weather website."*
* **Manual Verification:**
  * Look at the **Executive Telemetry** sidebar on the left.
  * The **Active Goal Anchor** should instantly update from `None` to:
    `"I need to write a Python script to scrape data from a weather website."`

---

### 🔧 Test 2: The Sub-Task (Dependency) Check
Verify that follow-up questions directly related to the root goal are processed as stable execution sub-tasks.

* **Interaction Type:** Sub-task / Query
* **User Input:** 
  > *"How do I install BeautifulSoup to do this?"*
* **Manual Verification:**
  * The AI should reply normally with installation instructions.
  * Look at the sidebar:
    * **Active Goal** must remain unchanged.
    * **Cognitive State** must remain green: **`⚡ STABLE COGNITIVE FLOW`**.
  * This confirms the backend recognized this as a dependency step for the root goal.

---

### ⚠️ Test 3: The Fragmentation (Attention) Check
Simulate a user sending rapid, short messages (often indicative of ADHD overwhelm or erratic typing) to trigger attention scaffolding.

* **Action:** Type and send the following three short messages rapidly (within 10 seconds total):
  1. **User Input:** `wait` ➔ Press **Enter**
  2. **User Input:** `errors` ➔ Press **Enter**
  3. **User Input:** `why isn't it working` ➔ Press **Enter**
* **Manual Verification:**
  * Look at the sidebar:
    * The **Cognitive State** should immediately flip to red: **`⚠️ FRAGMENTED ATTENTION DETECTED`**.
  * Look at the AI's response to your last message:
    * The response must be drastically shorter, using highly structured bullet points.
    * The AI must ask **only one simple question** at a time to reduce cognitive load and avoid overwhelming the user.

---

### 🚲 Test 4: The Tangent & Recovery Check
Verify that going off-topic isolates the conversation branch, and that the recovery mechanism restores focus to the main goal.

* **Interaction Type:** Tangent Detection & Recovery
* **User Input:** 
  > *"Actually, ignore the code for a second. What are the best settings for a TotGuard e-bike on steep hills?"*
* **Manual Verification:**
  1. **Tangent Behavior:** The AI should answer your e-bike question normally.
  2. **Recovery Prompt:** A button should dynamically appear at the bottom of the chat interface:
     `[ ↩️ Recover Goal: I need to write a Python script... ]`
  3. **Goal Restoration:** Click the recovery button.
     * The AI should automatically drop the e-bike conversation.
     * It will summarize that you took a detour and prompt you to pick up where you left off with the weather scraper.

---

## 📊 Phase 3: How to Visualize the DAG Graph

When you run through the session above, the backend constructs an interactive, mathematical Directed Acyclic Graph (DAG) representing your working memory. Follow these steps to inspect the graph.

### 🗺️ Step-by-Step Visualization

#### **Step 1: Generate the Map File**
1. In the Streamlit sidebar, locate the **"System Control Operations"** section.
2. Click the button: **`👁️ Compile Interactive DAG Map`**.
3. A success notification will appear.

#### **Step 2: Open the Map**
1. Open your operating system's file explorer.
2. Navigate to your project's root folder (`ADHD Cognitive Copilot`).
3. Locate the newly generated file: **`dag_visual.html`**.
4. Double-click **`dag_visual.html`** to open it in your web browser.

#### **Step 3: How to Read the Visualization**
The webpage shows a physics-based, interactive node-link map of your working memory. Nodes can be dragged and repositioned with your mouse.

* 🟩 **The Green Node (Root Anchor):** Represents your primary objective (the weather scraper).
* 🟦 **The Blue Nodes (Flow State Path):** Represents your main execution path (the BeautifulSoup setup, error troubleshooting).
* 🟧 **The Orange Nodes (Isolated Tangent):** Represents the e-bike tangent. Notice how this branch is isolated and separated from the main task path.
* 🟦 **The Final Blue Node (Restored State):** Created when you clicked **"Recover Goal"**. Notice how it links directly from the previous blue/green path, completely bypassing the orange tangent nodes.
