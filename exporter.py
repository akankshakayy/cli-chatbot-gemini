# exporter.py

from datetime import datetime

def export_markdown(messages: list, persona: str, session_id: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    filename  = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

    lines = [
        f"# Chat Export", f"",
        f"**Session:** `{session_id}`  ",
        f"**Persona:** {persona}  ",
        f"**Date:** {timestamp}  ",
        f"", f"---", f"",
    ]

    for msg in messages:
        text = msg["parts"][0]["text"]  # Gemini uses "parts" not "content"

        if text.startswith("[Summary of our earlier conversation"):
            continue
        if text.startswith("Understood. I have the context"):
            continue

        speaker = "**You**" if msg["role"] == "user" else "**Gemini**"
        lines += [speaker, "", text, "", "---", ""]

    content = "\n".join(lines)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename