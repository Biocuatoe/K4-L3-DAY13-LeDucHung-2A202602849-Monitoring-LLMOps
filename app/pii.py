from __future__ import annotations

import hashlib
import re
from typing import Any, Union

# Patterns must exactly match what scripts/validate_logs.py PII_DETECTORS greps for
# - email:    r"[\w.-]+@[\w.-]+\.\w+"
# - phone_vn: r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)"
# - cccd:     r"\b\d{12}\b"
# - credit_card: r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"
PII_PATTERNS: dict[str, str] = {
    "email": r"[\w.-]+@[\w.-]+\.\w+",
    "phone_vn": r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)",
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
}


def scrub_text(text: Union[str, bytes, int, float, Any]) -> str:
    """Scrub PII from text. Accepts any input type and return a string."""
    if isinstance(text, bytes):
        text = text.decode("utf-8", errors="replace")
    if not isinstance(text, str):
        text = str(text)

    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe)
    return safe


def summarize_text(text: Union[str, bytes, int, float, Any], max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
