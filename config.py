# config.py

# Gemini 2.0 Flash — fast, free, and very capable
MODEL = "gemini-2.5-flash"

# Max tokens the model can generate per reply
MAX_TOKENS = 1024

# Trigger summarization after this many messages
SUMMARY_THRESHOLD = 20

# How many recent messages to preserve after summarization
RECENT_MESSAGES_TO_KEEP = 6

# Folder where sessions are saved
SESSIONS_DIR = "sessions"

# Gemini 2.0 Flash pricing (for when you exceed free tier)
# Free tier: 1500 req/day. Paid: very cheap beyond that.
COST_INPUT_PER_1M  = 0.10   # $0.10 per 1M input tokens
COST_OUTPUT_PER_1M = 0.40   # $0.40 per 1M output tokens