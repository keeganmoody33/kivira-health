from __future__ import annotations

import re

LINKEDIN_PROFILE_RE = re.compile(
    r"^https?://(?:www\.)?linkedin\.com/in/[^/?#\s]+/?",
    re.IGNORECASE,
)
PHONEISH_RE = re.compile(r"^[\d\s().+\-]{7,}$")


def classify_col4(value: str) -> str:
    """Return linkedin | phone | empty | other."""
    s = (value or "").strip()
    if not s:
        return "empty"
    if LINKEDIN_PROFILE_RE.match(s):
        return "linkedin"
    if PHONEISH_RE.match(s):
        return "phone"
    if "linkedin.com" in s.lower():
        return "linkedin"
    return "other"


def normalize_linkedin_url(url: str) -> str:
    s = (url or "").strip()
    if not s:
        return ""
    if LINKEDIN_PROFILE_RE.match(s):
        return s.rstrip("/")
    return ""
