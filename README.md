# Multi-Persona CLI Chatbot

A terminal-based AI chatbot powered by Google Gemini with persistent sessions,
streaming responses, and multiple personas.

## Features
- Multi-turn conversations with full memory
- 5 built-in personas (default, tutor, critic, socratic, concise)
- Persistent sessions — resume any conversation later
- Streaming responses token by token
- Smart memory compression via summarization
- Token usage and cost tracking
- Export conversations as Markdown
- Slash command interface (/save, /load, /persona, /export, /cost)

## Setup

1. Clone the repo
   git clone https://github.com/yourname/cli-chatbot-gemini.git
   cd cli-chatbot-gemini

2. Create virtual environment
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies
   pip install -r requirements.txt

4. Get a free Gemini API key at aistudio.google.com
   export GEMINI_API_KEY="your-key-here"

5. Run it
   python3 chatbot.py

## Usage
   python3 chatbot.py                        # default persona
   python3 chatbot.py --persona tutor        # switch persona
   python3 chatbot.py --session my-chat      # named session
   python3 chatbot.py --session my-chat      # resume it next time

## Commands
   /help       show all commands
   /save       save current session
   /load <id>  load a saved session
   /sessions   list all saved sessions
   /persona    switch persona mid-conversation
   /cost       show token usage
   /export     save conversation as markdown
   /quit       exit