from __future__ import annotations

import re
from typing import Literal

FirstTouchCluster = Literal["A", "B", "C", "D", "E"]

PHYSICIAN_CRED_RE = re.compile(
    r"\b(?:m\.?d\.?|d\.?o\.?|doctor of medicine|doctor of osteopathy)\b",
    re.I,
)

CLUSTER_D_KEYWORDS = (
    "partnership",
    "partner",
    "business development",
    "channel",
    "enablement",
    "vp product",
    "vice president product",
    "director of growth",
    "dir of growth",
    "gm ",
    "general manager",
)

CLUSTER_C_KEYWORDS = (
    "care management",
    "care coordination",
    "care manager",
    "population health",
    "pop health",
    "bh navigation",
    "behavioral health navigation",
    "care navigator",
)

CLUSTER_B_KEYWORDS = (
    "quality",
    "risk adjustment",
    "risk ",
    "hedis",
    "stars",
    "raf",
    "vbc",
    "value-based",
    "value based",
    "medical director",  # plan-side often B; provider MD often A via subtier
    "chief medical officer",  # plan CMO → often B if health plan in company
)

CLUSTER_A_KEYWORDS = (
    "physician",
    "provider",
    "clinical director",
    "medical group",
    "primary care",
    "np ",
    "nurse practitioner",
    "physician assistant",
    " pa ",
    "behavioral health",
    "psychiatr",
)

FOUNDER_KEYWORDS = ("founder", "co-founder", "cofounder", "ceo at", "owner and president")


def _text(*parts: str) -> str:
    return " ".join(p for p in parts if p).lower()


def _has_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(k in text for k in keywords)


def is_physician_title(title: str, position: str = "") -> bool:
    combined = f"{title} {position}"
    if PHYSICIAN_CRED_RE.search(combined):
        return True
    if re.search(r"\b(?:md|do)\b", combined, re.I) and "medical director" not in combined.lower():
        return True
    return False


def format_address(first_name: str, last_name: str, title: str = "", position: str = "") -> str:
    """Dr. Lastname for physician creds; else first name."""
    last = (last_name or "").strip()
    first = (first_name or "").strip()
    if is_physician_title(title, position) and last:
        return f"Dr. {last}"
    return first or "there"


def classify_first_touch_cluster(
    title: str = "",
    *,
    persona: str = "",
    subtier: str = "",
    company: str = "",
    headline: str = "",
    about: str = "",
) -> tuple[FirstTouchCluster, str]:
    """Map a lead to playbook cluster A through E (role-first, subtier hint)."""
    text = _text(title, headline, about, company)
    st = (subtier or "").strip().upper()
    persona = (persona or "").strip()

    if _has_any(text, FOUNDER_KEYWORDS) and persona not in (
        "clinical_champion",
        "bh_quality_influencer",
        "operational_owner",
    ):
        return "E", "founder/ceo title signal"

    if st == "2B" or persona == "tech_gatekeeper" or _has_any(text, CLUSTER_D_KEYWORDS):
        return "D", f"partnership/channel (subtier={st or 'keywords'})"

    if st == "2C" or (
        persona == "operational_owner" and _has_any(text, CLUSTER_C_KEYWORDS)
    ):
        return "C", f"care coordination (subtier={st or 'ops+care keywords'})"

    if persona == "economic_buyer":
        return "B", "persona economic_buyer → VBC/risk"

    if st in ("1C", "2A", "3C") or _has_any(text, CLUSTER_B_KEYWORDS):
        if persona in ("clinical_champion", "bh_quality_influencer") and st in (
            "1A",
            "1B",
            "3A",
        ):
            return "A", "clinical persona at provider subtier"
        if st == "2A" and _has_any(text, ("behavioral health", "population health")):
            return "B", "2A plan/network with BH or pop-health title"
        return "B", f"VBC/risk (subtier={st or 'keywords'})"

    if st in ("1A", "1B", "3A") or persona in (
        "clinical_champion",
        "bh_quality_influencer",
    ):
        return "A", f"provider workflow (subtier={st or persona})"

    if persona == "operational_owner":
        if _has_any(text, CLUSTER_C_KEYWORDS):
            return "C", "operational_owner + care mgmt keywords"
        return "A", "operational_owner default → provider/ops workflow (cluster A)"

    if persona == "unknown":
        if _has_any(text, CLUSTER_B_KEYWORDS):
            return "B", "unknown persona + quality/risk keywords"
        if _has_any(text, CLUSTER_C_KEYWORDS):
            return "C", "unknown persona + care mgmt keywords"
        if _has_any(text, CLUSTER_A_KEYWORDS):
            return "A", "unknown persona + clinical keywords"
        return "E", "unknown persona, no strong title signal"

    return "E", "fallback cluster E"
