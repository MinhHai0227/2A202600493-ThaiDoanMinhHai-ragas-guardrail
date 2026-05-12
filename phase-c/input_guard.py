"""Phase C input guardrails: PII redaction + topic validator."""

from __future__ import annotations

import re
from dataclasses import dataclass


PII_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"\b(?:\+84|0)\d{9,10}\b"),
    "id_like": re.compile(r"\b\d{9,12}\b"),
}


@dataclass
class GuardResult:
    ok: bool
    sanitized_text: str
    reason: str


class InputGuard:
    def __init__(self, allowed_topics: tuple[str, ...] = ("dữ liệu", "nhân sự", "tài chính", "nghị định")):
        self.allowed_topics = allowed_topics

    def redact_pii(self, text: str) -> str:
        out = text
        for tag, pattern in PII_PATTERNS.items():
            out = pattern.sub(f"[REDACTED_{tag.upper()}]", out)
        return out

    def validate_topic(self, text: str) -> bool:
        lower = text.lower()
        return any(token in lower for token in self.allowed_topics)

    def check(self, text: str) -> GuardResult:
        sanitized = self.redact_pii(text)
        topic_ok = self.validate_topic(sanitized)
        if not topic_ok:
            return GuardResult(
                ok=False,
                sanitized_text=sanitized,
                reason="Query outside allowed domain topics.",
            )
        return GuardResult(ok=True, sanitized_text=sanitized, reason="ok")

