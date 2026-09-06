"""Deterministic detection for explicit outbound WhatsApp requests."""

from __future__ import annotations

import re

_CHANNEL_PATTERN = re.compile(r"\b(?:whatsapp|wa)\b", re.IGNORECASE)
_ACTION_PATTERN = re.compile(
    r"\b(?:"
    r"send|sent|remind|notify|ping|"
    r"send(?:e|en)?|schick(?:e|en|t)?|"
    r"erinner(?:e|n|t)?|benachrichtig(?:e|en|t)?"
    r")\b",
    re.IGNORECASE,
)
_QUESTION_PATTERN = re.compile(
    r"^(?:what|why|can|how|when|where|was|warum|kann|wie|wann|wo)\b",
    re.IGNORECASE,
)


def is_explicit_whatsapp_send_request(text: str | None) -> bool:
    """Return whether plain text explicitly asks to send or schedule WhatsApp.

    The check intentionally requires a WhatsApp/WA channel marker plus either
    an outbound action or scheduling language. It therefore does not route
    status questions such as "Why did my WhatsApp not arrive?".
    """
    normalized = (text or "").strip()
    if not normalized or normalized.startswith("/"):
        return False
    if not _CHANNEL_PATTERN.search(normalized):
        return False
    if normalized.endswith("?") or _QUESTION_PATTERN.search(normalized):
        return False
    return bool(_ACTION_PATTERN.search(normalized))
