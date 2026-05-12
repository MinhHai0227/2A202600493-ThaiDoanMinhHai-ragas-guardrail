"""Phase C output guardrail placeholder.

Replace this with Llama Guard 3 API/local model call for full lab scoring.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OutputGuardResult:
    safe: bool
    reason: str


class OutputGuard:
    BLOCK_KEYWORDS = ("self-harm", "kill", "attack", "hate", "terror")

    def check(self, user_input: str, answer: str) -> OutputGuardResult:
        text = f"{user_input}\n{answer}".lower()
        if any(token in text for token in self.BLOCK_KEYWORDS):
            return OutputGuardResult(safe=False, reason="Keyword policy trigger")
        return OutputGuardResult(safe=True, reason="ok")

