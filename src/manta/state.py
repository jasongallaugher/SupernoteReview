import json
import os
from datetime import datetime
from pathlib import Path

STATE_FILE = Path(".manta_state.json")

def load_state():
    if not STATE_FILE.exists():
        return {"reviews": {}}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def add_review(local_path, device_path):
    state = load_state()
    state["reviews"][str(local_path)] = {
        "device_path": device_path,
        "status": "pending",
        "timestamp": datetime.now().isoformat(),
        "original_path": str(Path(local_path).absolute())
    }
    save_state(state)

def get_pending_reviews():
    state = load_state()
    return {k: v for k, v in state["reviews"].items() if v["status"] == "pending"}

def mark_completed(local_path):
    state = load_state()
    if str(local_path) in state["reviews"]:
        state["reviews"][str(local_path)]["status"] = "completed"
        state["reviews"][str(local_path)]["completed_at"] = datetime.now().isoformat()
        save_state(state)
