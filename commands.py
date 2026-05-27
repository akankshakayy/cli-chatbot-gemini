# commands.py

from personas import list_personas

COMMANDS = {
    "/help"    : "Show this help message",
    "/save"    : "Save the current session",
    "/load"    : "/load <session-id> — Load a saved session",
    "/sessions": "List all saved sessions",
    "/clear"   : "Clear history and start fresh",
    "/persona" : "/persona <name> — Switch persona",
    "/personas": "List all available personas",
    "/cost"    : "Show token usage so far",
    "/export"  : "Export conversation as Markdown",
    "/quit"    : "Exit the chatbot",
}

def is_command(text: str) -> bool:
    return text.strip().startswith("/")

def parse_command(text: str) -> tuple[str, str]:
    parts = text.strip().split(maxsplit=1)
    cmd   = parts[0].lower()
    arg   = parts[1] if len(parts) > 1 else ""
    return cmd, arg

def handle_command(cmd: str, arg: str, app_state: dict) -> dict:
    from storage  import save_session, load_session, list_sessions
    from exporter import export_markdown
    from personas import get_persona, list_personas

    memory     = app_state["memory"]
    tracker    = app_state["tracker"]
    session_id = app_state["session_id"]
    persona    = app_state["persona"]

    if cmd == "/help":
        print("\nAvailable commands:")
        for c, desc in COMMANDS.items():
            print(f"  {c:<12} {desc}")
        print()

    elif cmd == "/save":
        path = save_session(session_id, memory.get_messages(), persona)
        print(f"\nSession saved to {path}\n")

    elif cmd == "/sessions":
        sessions = list_sessions()
        if not sessions:
            print("\nNo saved sessions found.\n")
        else:
            print(f"\n{'ID':<20} {'Persona':<12} {'Turns':<8} Saved at")
            print("-" * 60)
            for s in sessions:
                print(f"{s['id']:<20} {s['persona']:<12} {s['turns']:<8} {s['saved_at'][:16]}")
            print()

    elif cmd == "/load":
        if not arg:
            print("\nUsage: /load <session-id>\n")
        else:
            data = load_session(arg)
            if data is None:
                print(f"\nNo session found with id '{arg}'\n")
            else:
                memory.set_messages(data["messages"])
                app_state["persona"]    = data["persona"]
                app_state["session_id"] = arg
                print(f"\nLoaded session '{arg}'\n")

    elif cmd == "/clear":
        memory.set_messages([])
        print("\nHistory cleared.\n")

    elif cmd == "/persona":
        if not arg:
            print(f"\nCurrent persona: {persona}")
            print(f"Available: {', '.join(list_personas())}\n")
        else:
            system_prompt          = get_persona(arg)
            app_state["persona"]       = arg
            app_state["system_prompt"] = system_prompt
            print(f"\nPersona switched to '{arg}'.\n")

    elif cmd == "/personas":
        print(f"\nAvailable personas: {', '.join(list_personas())}\n")

    elif cmd == "/cost":
        print(tracker.session_summary())

    elif cmd == "/export":
        filename = export_markdown(memory.get_messages(), persona, session_id)
        print(f"\nExported to {filename}\n")

    elif cmd == "/quit":
        app_state["running"] = False

    else:
        print(f"\nUnknown command '{cmd}'. Type /help for a list.\n")

    return app_state