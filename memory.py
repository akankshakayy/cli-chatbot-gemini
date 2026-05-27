# memory.py

import google.genai as genai
import google.genai.types as types
from config import MODEL, MAX_TOKENS, SUMMARY_THRESHOLD, RECENT_MESSAGES_TO_KEEP

class ConversationMemory:
    """
    Manages conversation history for Gemini.

    KEY DIFFERENCE FROM ANTHROPIC:
    Gemini uses "model" as the role name for AI responses.
    Anthropic uses "assistant". Everything else is the same concept.

    Gemini message format:
    [
        {"role": "user",  "parts": [{"text": "Hello"}]},
        {"role": "model", "parts": [{"text": "Hi there!"}]},
    ]

    Note the "parts" wrapper — Gemini supports multimodal content
    (text, images, audio) so each message is a list of "parts".
    For text-only chatbots, each part is just {"text": "..."}.
    """

    def __init__(self):
        self.messages = []

    def add_user(self, content: str):
        self.messages.append({
            "role": "user",
            "parts": [{"text": content}]
        })

    def add_assistant(self, content: str):
        # Gemini uses "model" not "assistant"
        self.messages.append({
            "role": "model",
            "parts": [{"text": content}]
        })

    def get_messages(self) -> list:
        return self.messages

    def set_messages(self, messages: list):
        self.messages = messages

    def should_summarize(self) -> bool:
        return len(self.messages) >= SUMMARY_THRESHOLD

    def summarize(self, client: genai.Client):
        """
        Summarize old messages to compress history.
        Same logic as Anthropic version — calls Gemini to summarize,
        replaces old messages with a compact summary block.
        """
        print("\n\033[90m[Compressing conversation history...]\033[0m")

        recent = self.messages[-RECENT_MESSAGES_TO_KEEP:]
        old    = self.messages[:-RECENT_MESSAGES_TO_KEEP]

        if not old:
            return

        # Call Gemini to summarize old messages
        response = client.models.generate_content(
            model=MODEL,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are a conversation summarizer. Summarize the following "
                    "conversation in 4-6 sentences. Preserve: the user's name if "
                    "mentioned, key facts they shared, decisions made, and main topics."
                ),
                max_output_tokens=400,
            ),
            contents=old
        )
        summary_text = response.text

        summary_block = [
            {
                "role": "user",
                "parts": [{"text": f"[Summary of our earlier conversation: {summary_text}]"}]
            },
            {
                "role": "model",
                "parts": [{"text": "Understood. I have the context from our earlier conversation."}]
            }
        ]

        self.messages = summary_block + recent
        print(f"\033[90m[History compressed: {len(old)} messages → 2 summary blocks]\033[0m\n")