"""CoCM estimation logic."""

from __future__ import annotations

import json
from pathlib import Path

from tam_builder.adapters import PublicSignalAdapter
from tam_builder.briefing import build_outbound_message
from tam_builder.constants import CAVEATS, DEFAULT_PERSONA_SEQUENCE, ESTIMATE_FIELDS, SCENARIO_ASSUMPTIONS
from tam_builder.io_utils import ensure_directory, parse_pipe_list, slugify, write_csv, write_json
from tam_builder.personas import merge_persona_priorities


def estimate_accounts(
    rows: list[dict[str, object]],
    adapter: PublicSignalAdapter,
    artifact_dir: str | Path,
    include_low_confidence: bool = False,
) -> list[dict[str, object]]:
    artifact_root = ensure_directory(artifact_dir)
    estimates: list[dict[str, object]] = []
    for row in rows:
        estimate, provider_rows = estimate_account(row, adapter, include_low_confidence)
        write_account_artifacts(estimate, provider_rows, artifact_root)
        estimates.append(estimate)
    return estimates


def estimate_account(
    row: dict[str, object],
    adapter: PublicSignalAdapter,
    include_low_confidence: bool = False,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    adapter_result = adapter.collect(row, include_low_confidence=include_low_confidence)
    enriched = dict(row)
    enriched.update(adapter_result.account_updates)

    high = int(float(enriched.get("high_confidence_clinicians", 0) or 0))
    medium = int(float(enriched.get("medium_confidence_clinicians", 0) or 0))
    low = int(float(enriched.get("low_confidence_clinicians", 0) or 0))
    matched = high + medium + low
    observed_g0444 = int(float(enriched.get("observed_g0444_benes", 0) or 0))
    observed_96127 = int(float(enriched.get("observed_96127_benes", 0) or 0))
    observed_cocm_benes = int(float(enriched.get("observed_cocm_benes", 0) or 0))
    observed_cocm_services = int(float(enriched.get("observed_cocm_services", 0) or 0))
    observed_cocm_revenue = float(enriched.get("observed_cocm_revenue", 0.0) or 0.0)
    identity_quality = str(enriched.get("identity_match_quality", "weak"))
    blended_penalty = bool(enriched.get("experimental_blended_denominator", False))
    cocm_visibility = "reported" if any((observed_cocm_benes, observed_cocm_services, observed_cocm_revenue)) else "not_reported_or_suppressed"

    score = confidence_score(
        high=high,
        medium=medium,
        low=low,
        observed_g0444=observed_g0444,
        identity_quality=identity_quality,
        cocm_visibility=cocm_visibility,
        blended_penalty=blended_penalty,
    )
    grade = confidence_grade(score)
    screening_proxy = max(observed_g0444, observed_96127)

    scenarios = SCENARIO_ASSUMPTIONS[str(enriched.get("org_type", ""))]
    conservative_gap = modeled_gap(screening_proxy, scenarios["conservative"], observed_cocm_revenue)
    base_gap = modeled_gap(screening_proxy, scenarios["base"], observed_cocm_revenue)
    aggressive_gap = modeled_gap(screening_proxy, scenarios["aggressive"], observed_cocm_revenue)

    persona_messages = build_persona_messages(enriched, grade, conservative_gap, base_gap, aggressive_gap, screening_proxy)

    estimate = dict(enriched)
    estimate.update(
        {
            "matched_clinicians": matched,
            "cocm_visibility": cocm_visibility,
            "screening_proxy_benes": screening_proxy,
            "conservative_gap": conservative_gap,
            "base_gap": base_gap,
            "aggressive_gap": aggressive_gap,
            "confidence_score": score,
            "confidence_grade": grade,
            "caveats": json.dumps(list(CAVEATS), sort_keys=True),
            "persona_messages": json.dumps(persona_messages, sort_keys=True),
        }
    )
    return ordered_estimate(estimate), adapter_result.provider_debug_rows


def confidence_score(
    *,
    high: int,
    medium: int,
    low: int,
    observed_g0444: int,
    identity_quality: str,
    cocm_visibility: str,
    blended_penalty: bool,
) -> int:
    score = 0
    total = high + medium + low
    if high >= 10:
        score += 35
    elif high >= 5:
        score += 25
    elif high + medium >= 5:
        score += 15
    elif total >= 3:
        score += 5

    if observed_g0444 >= 100:
        score += 25
    elif observed_g0444 >= 50:
        score += 20
    elif observed_g0444 >= 20:
        score += 12
    elif observed_g0444 > 0:
        score += 5

    if identity_quality == "strong":
        score += 20
    elif identity_quality == "moderate":
        score += 10

    score += 10 if cocm_visibility == "reported" else 5
    if blended_penalty:
        score -= 10
    return score


def confidence_grade(score: int) -> str:
    if score >= 80:
        return "A"
    if score >= 55:
        return "B"
    if score >= 30:
        return "C"
    return "D"


def modeled_gap(screening_proxy: int, scenario, observed_cocm_revenue: float) -> float:
    modeled_revenue = screening_proxy * scenario.activation_rate * scenario.monthly_payment * scenario.treatment_months
    return round(max(modeled_revenue - observed_cocm_revenue, 0.0), 2)


def build_persona_messages(
    row: dict[str, object],
    grade: str,
    conservative_gap: float,
    base_gap: float,
    aggressive_gap: float,
    screening_proxy: int,
) -> dict[str, str]:
    org_type = str(row.get("org_type", ""))
    preferred = parse_pipe_list(str(row.get("priority_personas", "")))
    default_sequence = list(DEFAULT_PERSONA_SEQUENCE.get(org_type, ()))
    personas = merge_persona_priorities(preferred, default_sequence)
    messages: dict[str, str] = {}
    org_name = str(row.get("org_name", "this account"))
    for persona in personas:
        messages[persona] = build_outbound_message(
            org_name,
            persona,
            grade,
            screening_proxy,
            conservative_gap,
            base_gap,
            aggressive_gap,
        )
    return messages


def write_account_artifacts(
    estimate: dict[str, object],
    provider_rows: list[dict[str, object]],
    artifact_root: Path,
) -> None:
    account_slug = slugify(str(estimate.get("org_name", "")))
    summary_csv_path = artifact_root / f"{account_slug}_estimate.csv"
    summary_json_path = artifact_root / f"{account_slug}_estimate.json"
    debug_csv_path = artifact_root / f"{account_slug}_provider_debug.csv"
    write_csv(summary_csv_path, [estimate], ESTIMATE_FIELDS)
    write_json(
        summary_json_path,
        {
            "org_name": estimate.get("org_name", ""),
            "state": estimate.get("state", ""),
            "city": estimate.get("city", ""),
            "org_type": estimate.get("org_type", ""),
            "priority_personas": parse_pipe_list(str(estimate.get("priority_personas", ""))),
            "observed_metrics": {
                "matched_clinicians": estimate.get("matched_clinicians", 0),
                "high_confidence_clinicians": estimate.get("high_confidence_clinicians", 0),
                "observed_g0444_benes": estimate.get("observed_g0444_benes", 0),
                "observed_96127_benes": estimate.get("observed_96127_benes", 0),
                "observed_cocm_benes": estimate.get("observed_cocm_benes", 0),
                "observed_cocm_services": estimate.get("observed_cocm_services", 0),
                "observed_cocm_revenue": estimate.get("observed_cocm_revenue", 0),
            },
            "modeled_opportunity": {
                "screening_proxy_benes": estimate.get("screening_proxy_benes", 0),
                "conservative_gap": estimate.get("conservative_gap", 0),
                "base_gap": estimate.get("base_gap", 0),
                "aggressive_gap": estimate.get("aggressive_gap", 0),
            },
            "confidence_grade": estimate.get("confidence_grade", ""),
            "confidence_score": estimate.get("confidence_score", 0),
            "caveats": json.loads(str(estimate.get("caveats", "[]"))),
            "persona_messages": json.loads(str(estimate.get("persona_messages", "{}"))),
        },
    )
    write_csv(
        debug_csv_path,
        provider_rows,
        [
            "org_name",
            "state",
            "city",
            "provider_npi",
            "provider_name",
            "match_confidence",
            "affiliation_score",
            "match_reason",
            "observed_g0444_benes",
            "observed_96127_benes",
            "observed_cocm_benes",
            "observed_cocm_services",
            "observed_cocm_revenue",
        ],
    )


def ordered_estimate(row: dict[str, object]) -> dict[str, object]:
    ordered = {field: row.get(field, "") for field in ESTIMATE_FIELDS}
    for key, value in row.items():
        if key not in ordered:
            ordered[key] = value
    return ordered
