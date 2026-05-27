# chat_engine.py

import time
import google.genai as genai
import google.genai.types as types
from config import MODEL, MAX_TOKENS

def stream_response(
    client: genai.Client,
    system_prompt: str,
    messages: list
) -> tuple[str, int, int]:
    """
    Stream a response from Gemini token by token.

    HOW GEMINI'S API DIFFERS FROM ANTHROPIC:

    Anthropic:
        client.messages.stream(model=..., system=..., messages=...)

    Gemini:
        client.models.generate_content_stream(
            model=...,
            config=GenerateContentConfig(system_instruction=..., ...),
            contents=...   ← the message history
        )

    The system prompt goes inside a config object, not as a top-level param.
    The message history is called "contents" not "messages".
    
    Token counts: Gemini returns usage_metadata on the final chunk,
    with prompt_token_count and candidates_token_count.
    """
    print("\nGemini: ", end="", flush=True)

    full_reply    = ""
    input_tokens  = 0
    output_tokens = 0

    # GenerateContentConfig holds model settings
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        max_output_tokens=MAX_TOKENS,
        temperature=0.7,   # 0 = deterministic, 1 = creative, 0.7 is a good default
    )

    for chunk in client.models.generate_content_stream(
        model=MODEL,
        config=config,
        contents=messages   # the full conversation history
    ):
        # Each chunk has a .text property with the new tokens
        if chunk.text:
            print(chunk.text, end="", flush=True)
            full_reply += chunk.text

        # The last chunk contains token usage metadata
        if chunk.usage_metadata:
            input_tokens  = chunk.usage_metadata.prompt_token_count or 0
            output_tokens = chunk.usage_metadata.candidates_token_count or 0

    print("\n")
    return full_reply, input_tokens, output_tokens


def call_with_retry(
    client: genai.Client,
    system_prompt: str,
    messages: list,
    max_retries: int = 3
) -> tuple[str, int, int]:
    """
    Retry wrapper with exponential backoff for Gemini API errors.
    
    Gemini raises google.api_core.exceptions for most errors.
    We handle the most common ones:
    - ResourceExhausted: rate limit hit (429)
    - ServiceUnavailable: server overloaded (503)
    - InvalidArgument: bad request — not retryable
    """
    import google.api_core.exceptions as gexc

    for attempt in range(max_retries):
        try:
            return stream_response(client, system_prompt, messages)

        except gexc.ResourceExhausted:
            # Free tier rate limit — wait and retry
            wait = 2 ** attempt
            print(f"\n\033[93mRate limit hit. Retrying in {wait}s...\033[0m")
            time.sleep(wait)

        except gexc.ServiceUnavailable:
            wait = 2 ** attempt
            print(f"\n\033[93mService unavailable. Retrying in {wait}s...\033[0m")
            time.sleep(wait)

        except gexc.InvalidArgument as e:
            # Bad request — retrying won't help
            print(f"\n\033[91mInvalid request: {e}\033[0m")
            raise

        except Exception as e:
            print(f"\n\033[91mUnexpected error: {e}\033[0m")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise

    raise RuntimeError("Max retries exceeded.")