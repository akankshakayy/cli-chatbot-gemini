# cost_tracker.py

from config import COST_INPUT_PER_1M, COST_OUTPUT_PER_1M

class CostTracker:
    """
    Tracks token usage and estimated cost.
    
    Gemini's free tier means cost is $0 under 1500 req/day.
    This tracker still counts tokens so you can see usage,
    and estimates cost for if/when you go beyond the free tier.
    """

    def __init__(self):
        self.total_input_tokens  = 0
        self.total_output_tokens = 0
        self.total_cost          = 0.0
        self.turn_count          = 0

    def record(self, input_tokens: int, output_tokens: int):
        self.total_input_tokens  += input_tokens
        self.total_output_tokens += output_tokens
        self.turn_count          += 1

        # Gemini pricing is per 1M tokens (not 1K like Anthropic)
        turn_cost = (
            (input_tokens  / 1_000_000) * COST_INPUT_PER_1M +
            (output_tokens / 1_000_000) * COST_OUTPUT_PER_1M
        )
        self.total_cost += turn_cost
        return turn_cost

    def turn_summary(self, turn_cost: float, input_tokens: int, output_tokens: int) -> str:
        return (
            f"  \033[90m[in: {input_tokens} | out: {output_tokens} | "
            f"est. cost: ${turn_cost:.6f} | session: ${self.total_cost:.5f}]"
            f" (free tier)\033[0m"
        )

    def session_summary(self) -> str:
        return (
            f"\n--- Session summary ---\n"
            f"Turns        : {self.turn_count}\n"
            f"Input tokens : {self.total_input_tokens:,}\n"
            f"Output tokens: {self.total_output_tokens:,}\n"
            f"Est. cost    : ${self.total_cost:.5f} (likely $0 on free tier)\n"
        )