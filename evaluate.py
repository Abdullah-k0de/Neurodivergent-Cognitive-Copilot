import requests
import time
import sys
import os

URL = "http://127.0.0.1:8000"

def run_evaluation_suite():
    print("🚀 Initializing Programmatic Architecture Validation Protocol...\n")
    try:
        requests.post(f"{URL}/reset")
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Backend server is offline. Start the uvicorn process first.")
        sys.exit(1)

    print("Evaluating Metric 1: Root Anchor Locking...")
    init_payload = {"user_input": "Implement memory layout logic matching the fifty percent paging rule."}
    res = requests.post(f"{URL}/chat", params=init_payload).json()
    state = res["state"]
    if state["active_primary_goal"] == init_payload["user_input"]:
        print("✅ PASS: Primary goal context securely mapped to root anchor pointer.")
    else:
        print("❌ FAIL: Structural boundary mapping anomaly.")
        sys.exit(1)
        
    print("\nEvaluating Metric 2: Fragmentation Speed Heuristics...")
    inputs = ["wait", "errors?", "why"]
    for idx, prompt in enumerate(inputs):
        time.sleep(0.4)
        res = requests.post(f"{URL}/chat", params={"user_input": prompt}).json()
    if res["state"]["cognitive_state"] == "fragmented":
        print("✅ PASS: Dynamic behavioral rules successfully identified user focus strain.")
    else:
        print("❌ FAIL: Adaptive cadence monitoring gate variance anomaly.")
        sys.exit(1)

    print("\nEvaluating Metric 3: Branch Isolation & Context Teleporting...")
    requests.post(f"{URL}/chat", params={"user_input": "What's the absolute best torque ratio for TotGuard electronic bicycle tires?"}).json()
    rec_res = requests.post(f"{URL}/recover-root").json()
    if rec_res["state"]["cognitive_state"] == "flow" and rec_res["state"]["current_node_id"] != state["current_node_id"]:
        print("✅ PASS: Tangent branch isolated. Extraction logic safely appended synthesis node.")
    else:
        print("❌ FAIL: Recovery engine state configuration error.")
        sys.exit(1)

    print("\nEvaluating Metric 4: Visualization Mapping Export...")
    requests.get(f"{URL}/visualize")
    if os.path.exists("dag_visual.html"):
        print("✅ PASS: Topology network maps exported successfully to 'dag_visual.html'.")
    else:
        print("❌ FAIL: Output stream execution barrier detected.")
        sys.exit(1)

    print("\n🎉 STRUCTURE CONSTRAINTS VALIDATED: ALL PIPELINES FUNCTIONAL.")

if __name__ == "__main__":
    run_evaluation_suite()