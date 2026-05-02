"""Tiering logic for the CoCM deployment guide."""

from __future__ import annotations


def tier_account_row(row: dict[str, object]) -> dict[str, object]:
    enriched = dict(row)
    base_gap = float(row.get("base_gap", 0) or 0)
    g0444_benes = int(float(row.get("observed_g0444_benes", 0) or 0))
    high_conf = int(float(row.get("high_confidence_clinicians", 0) or 0))
    grade = str(row.get("confidence_grade", "D"))

    tier = determine_tier(grade, base_gap, high_conf)
    numeric_claims_allowed = grade in {"A", "B"}

    enriched["tier"] = tier
    enriched["tier_score"] = round((base_gap / 1000.0) + (high_conf * 5.0) + (g0444_benes * 0.5), 2)
    enriched["numeric_claims_allowed"] = numeric_claims_allowed
    if tier == "Tier 1":
        enriched["outbound_eligibility_status"] = "eligible"
        enriched["outbound_recommendation"] = (
            "Week 1 clinical outreach, Week 2 finance follow-up with caveated range, Week 3 informatics thread."
        )
    elif tier == "Tier 2":
        enriched["outbound_eligibility_status"] = "eligible"
        enriched["outbound_recommendation"] = (
            "Start with the clinical buyer only. Keep modeled numbers as verbal support unless confidence strengthens."
        )
    elif tier == "Tier 3":
        enriched["outbound_eligibility_status"] = "nurture_only"
        enriched["outbound_recommendation"] = (
            "Nurture only. Use the category story and re-run when fresh public data or stronger validation appears."
        )
    else:
        enriched["outbound_eligibility_status"] = "qualify_elsewhere"
        enriched["outbound_recommendation"] = "Do not outbound on public-signal logic alone."
    return enriched


def determine_tier(grade: str, base_gap: float, high_conf: int) -> str:
    if grade == "D" or base_gap < 10_000:
        return "Tier 4"
    if grade in {"A", "B"} and base_gap > 75_000 and high_conf >= 10:
        return "Tier 1"
    if grade in {"B", "C"} and 25_000 <= base_gap <= 75_000 and high_conf >= 5:
        return "Tier 2"
    if grade == "C" and 10_000 <= base_gap < 25_000:
        return "Tier 3"
    if grade in {"A", "B"} and base_gap >= 25_000 and high_conf >= 5:
        return "Tier 2"
    if base_gap >= 10_000:
        return "Tier 3"
    return "Tier 4"
