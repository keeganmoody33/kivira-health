from __future__ import annotations

from typing import Literal

from tam_builder.josh_pilot.read_buckets import (
    INTEGRATED_CARE_KEYWORDS,
    OPS_KEYWORDS,
    ROI_KEYWORDS,
    match_read_bucket,
)

MessageLane = Literal["clinical", "roi", "ops"]


def _has_any(text: str, keywords: tuple[str, ...]) -> bool:
    t = text.lower()
    return any(k in t for k in keywords)


def classify_message_lane(
    title: str,
    *,
    persona: str = "",
    headline: str = "",
    about: str = "",
) -> tuple[MessageLane, str]:
    """Assign clinical | roi | ops with rationale."""
    combined = " ".join(filter(None, [title, headline, about]))
    read_bucket = match_read_bucket(combined)

    if _has_any(combined, INTEGRATED_CARE_KEYWORDS) or persona in (
        "bh_quality_influencer",
        "clinical_champion",
    ):
        return "clinical", f"READ/clinical signals ({read_bucket or 'keywords'})"

    if _has_any(combined, ROI_KEYWORDS) or persona == "economic_buyer":
        if _has_any(combined, INTEGRATED_CARE_KEYWORDS):
            return "clinical", "BH language overrides economic title"
        return "roi", f"READ/revenue signals ({read_bucket or 'persona economic_buyer'})"

    if _has_any(combined, OPS_KEYWORDS) or persona == "operational_owner":
        return "ops", f"READ/ops signals ({read_bucket or 'persona operational_owner'})"

    if persona == "tech_gatekeeper":
        return "ops", "tech gatekeeper → implementation/ops framing"

    if read_bucket == "integrated_care":
        return "clinical", "READ bucket integrated_care"
    if read_bucket == "regulatory_revenue":
        return "roi", "READ bucket regulatory_revenue"
    if read_bucket == "service_line":
        return "ops", "READ bucket service_line"

    return "ops", "default ops lane (ambiguous title)"
