# storage.py

import json
import os
from datetime import datetime
from config import SESSIONS_DIR

def ensure_sessions_dir():
    os.makedirs(SESSIONS_DIR, exist_ok=True)

def save_session(session_id: str, messages: list, persona: str) -> str:
    ensure_sessions_dir()
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    data = {
        "session_id": session_id,
        "persona"   : persona,
        "saved_at"  : datetime.now().isoformat(),
        "messages"  : messages
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return filepath

def load_session(session_id: str) -> dict | None:
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def list_sessions() -> list[dict]:
    ensure_sessions_dir()
    sessions = []
    for filename in os.listdir(SESSIONS_DIR):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(SESSIONS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            sessions.append({
                "id"      : data.get("session_id", filename[:-5]),
                "persona" : data.get("persona", "default"),
                "saved_at": data.get("saved_at", "unknown"),
                "turns"   : len(data.get("messages", [])) // 2
            })
    return sorted(sessions, key=lambda s: s["saved_at"], reverse=True)

def delete_session(session_id: str) -> bool:
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False