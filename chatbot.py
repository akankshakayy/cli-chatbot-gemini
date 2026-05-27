# chatbot.py

import argparse
import google.genai as genai
from datetime import datetime

from config       import MODEL
from personas     import get_persona
from memory       import ConversationMemory
from storage      import load_session
from commands     import is_command, parse_command, handle_command
from chat_engine  import call_with_retry
from cost_tracker import CostTracker

def parse_args():
    parser = argparse.ArgumentParser(
        description="A multi-persona CLI chatbot powered by Gemini (free tier)."
    )
    parser.add_argument("--persona",  default="default", help="Persona to use.")
    parser.add_argument("--session",  default=None,      help="Session ID to load or create.")
    return parser.parse_args()

def print_welcome(persona: str, session_id: str):
    print("\n" + "="*50)
    print("  CLI Chatbot  (Gemini — free tier)")
    print(f"  Persona : {persona}")
    print(f"  Session : {session_id}")
    print(f"  Model   : {MODEL}")
    print("  Type /help for commands, /quit to exit")
    print("="*50 + "\n")

def main():
    args = parse_args()
    session_id = args.session or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Initialize the Gemini client
    # Reads GEMINI_API_KEY from your environment automatically
    client = genai.Client()

    memory        = ConversationMemory()
    tracker       = CostTracker()
    persona       = args.persona
    system_prompt = get_persona(persona)

    if args.session:
        data = load_session(args.session)
        if data:
            memory.set_messages(data["messages"])
            persona       = data.get("persona", persona)
            system_prompt = get_persona(persona)
            print(f"Resuming session '{args.session}' ({len(data['messages'])//2} turns)")

    print_welcome(persona, session_id)

    app_state = {
        "memory"       : memory,
        "persona"      : persona,
        "system_prompt": system_prompt,
        "session_id"   : session_id,
        "tracker"      : tracker,
        "client"       : client,
        "running"      : True,
    }

    while app_state["running"]:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nInterrupted.")
            break

        if not user_input:
            continue

        if is_command(user_input):
            cmd, arg  = parse_command(user_input)
            app_state = handle_command(cmd, arg, app_state)
            persona       = app_state["persona"]
            system_prompt = app_state["system_prompt"]
            continue

        memory.add_user(user_input)

        if memory.should_summarize():
            memory.summarize(client)

        try:
            reply, input_tokens, output_tokens = call_with_retry(
                client,
                system_prompt,
                memory.get_messages()
            )
        except Exception as e:
            print(f"\n\033[91mError: {e}\033[0m\n")
            memory.messages.pop()
            continue

        memory.add_assistant(reply)
        turn_cost = tracker.record(input_tokens, output_tokens)
        print(tracker.turn_summary(turn_cost, input_tokens, output_tokens))
        print()

    print(tracker.session_summary())

if __name__ == "__main__":
    main()