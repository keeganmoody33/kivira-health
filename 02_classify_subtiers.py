#!/usr/bin/env python3
"""
02_classify_subtiers.py

Classify seeded healthcare accounts into Kivira 9-subtier GTM architecture.

Inputs (defaults under ./output/):
- output/accounts_seed_GA.csv
- output/accounts_seed_NC.csv
- optional reference files under ./input or ./output

Outputs (under output_dir/output/):
- accounts_classified_GA.csv
- accounts_classified_NC.csv
- accounts_classified_all.csv
- classification_review_queue.csv
- classification_exclusions.csv
- subtier_summary_by_state.csv

Dependencies: pandas, rapidfuzz, python-dateutil, requests (optional), standard library.
No paid enrichment. Account-level only.
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd
from dateutil.parser import isoparse

try:
    from rapidfuzz import fuzz as _rapidfuzz_fuzz  # type: ignore
except Exception:  # noqa: BLE001
    _rapidfuzz_fuzz = None


LOGGER = logging.getLogger("kivira.classify")


OUTPUT_COLUMNS: List[str] = [
    "account_id",
    "org_name",
    "parent_org_id",
    "entity_type",
    "practice_state",
    "mailing_state",
    "primary_state",
    "all_states_seen",
    "multi_state_flag",
    "subtier_primary",
    "subtier_secondary_tags",
    "tier_bucket",
    "classification_confidence",
    "classification_status",
    "classification_reason",
    "vbc_signal",
    "aco_signal",
    "payer_signal",
    "provider_group_signal",
    "health_system_signal",
    "idn_signal",
    "care_management_signal",
    "enablement_signal",
    "bh_signal",
    "size_signal",
    "pcp_count_est",
    "site_count_est",
    "covered_lives_est",
    "exclude_flag",
    "exclusion_reason",
    "review_flag",
    "review_reason",
    "evidence_urls",
    "evidence_notes",
    "last_verified_at",
    "website",
    "phone_main",
]


SUBTIERS: List[str] = ["1A", "1B", "1C", "2A", "2B", "2C", "3A", "3B", "3C"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_iso_or_none(value: str | None) -> Optional[datetime]:
    if not value:
        return None
    try:
        return isoparse(value)
    except Exception:
        return None


# ---------------------------
# Pure functions (unit-testable)
# ---------------------------
def normalize_org_name(name: str) -> str:
    if not name:
        return ""
    cleaned = []
    for ch in name.strip():
        if ch.isalnum() or ch.isspace():
            cleaned.append(ch.upper())
        else:
            cleaned.append(" ")
    out = " ".join("".join(cleaned).split())
    for suffix in [" LLC", " PLLC", " INC", " INCORPORATED", " PC", " PA", " LLP", " LP", " LTD", " CO", " CORP", " CORPORATION"]:
        if out.endswith(suffix):
            out = out[: -len(suffix)].rstrip()
    return out


def token_sort_ratio(a: str, b: str) -> int:
    a = (a or "").strip()
    b = (b or "").strip()
    if not a and not b:
        return 100
    if _rapidfuzz_fuzz is not None:
        return int(_rapidfuzz_fuzz.token_sort_ratio(a, b))
    import difflib

    def norm_tokens(s: str) -> str:
        toks = [t for t in s.upper().split() if t]
        toks.sort()
        return " ".join(toks)

    aa = norm_tokens(a)
    bb = norm_tokens(b)
    return int(round(difflib.SequenceMatcher(a=aa, b=bb).ratio() * 100))


def safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return float(s)
    except Exception:
        return None


def safe_int(value: Any) -> Optional[int]:
    f = safe_float(value)
    if f is None:
        return None
    try:
        return int(round(f))
    except Exception:
        return None


def as_bool_str(value: bool) -> str:
    return "true" if value else "false"


def json_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x) for x in value if str(x).strip()]
    s = str(value).strip()
    if not s:
        return []
    try:
        parsed = json.loads(s)
        if isinstance(parsed, list):
            return [str(x) for x in parsed if str(x).strip()]
    except Exception:
        pass
    # Fall back to pipe delim
    return [p.strip() for p in s.split("|") if p.strip()]


@dataclass(frozen=True)
class Thresholds:
    pcp_floor_1a: int = 5
    pcp_floor_1b: int = 3
    sites_floor_1a: int = 2
    employed_pcp_floor_3a: int = 50
    sites_floor_3a: int = 3
    covered_lives_min_2a: int = 500

    review_delta: float = 0.10


@dataclass(frozen=True)
class KeywordSignals:
    payer_keywords: Tuple[str, ...] = (
        "BLUE CROSS",
        "BCBS",
        "HEALTH PLAN",
        "MEDICARE ADVANTAGE",
        "MCO",
        "MEDICAID",
        "HEALTH INSURANCE",
        "HMO",
        "PAYER",
    )
    health_system_keywords: Tuple[str, ...] = (
        "HEALTH SYSTEM",
        "HOSPITAL",
        "MEDICAL CENTER",
        "REGIONAL MEDICAL",
        "MEMORIAL HOSPITAL",
        "CLINIC AND HOSPITAL",
    )
    idn_keywords: Tuple[str, ...] = (
        "INTEGRATED DELIVERY",
        "IDN",
        "NETWORK",
        "SYSTEM OF CARE",
    )
    enablement_keywords: Tuple[str, ...] = (
        "VALUE BASED",
        "RISK",
        "QUALITY",
        "ANALYTICS",
        "CARE ORCHESTRATION",
        "POPULATION HEALTH",
        "CARE PLATFORM",
        "RISK ADJUSTMENT",
        "NAVIGATION",
    )
    care_mgmt_keywords: Tuple[str, ...] = (
        "CARE MANAGEMENT",
        "CARE COORDINATION",
        "CHRONIC CARE",
        "CCM",
        "TRANSITIONAL CARE",
        "TCM",
        "NAVIGATION",
        "POST ACUTE",
    )
    d2c_telehealth_keywords: Tuple[str, ...] = (
        "TELEHEALTH",
        "VIRTUAL CARE",
        "DIRECT TO CONSUMER",
        "DTC",
    )


@dataclass(frozen=True)
class ReferenceSets:
    aco_reach_names: Tuple[str, ...] = ()
    mssp_aco_names: Tuple[str, ...] = ()
    health_system_names: Tuple[str, ...] = ()
    regional_payer_names: Tuple[str, ...] = ()
    enablement_names: Tuple[str, ...] = ()
    care_management_names: Tuple[str, ...] = ()

    # Normalized fast lookup
    aco_reach_norm: frozenset[str] = frozenset()
    mssp_aco_norm: frozenset[str] = frozenset()
    health_system_norm: frozenset[str] = frozenset()
    regional_payer_norm: frozenset[str] = frozenset()
    enablement_norm: frozenset[str] = frozenset()
    care_management_norm: frozenset[str] = frozenset()


def score_subtier(subtier: str, signals: Dict[str, Any], thresholds: Thresholds) -> Tuple[float, str]:
    """
    Return (score 0..1, evidence_note).
    """
    pcp = safe_int(signals.get("pcp_count_est")) or 0
    sites = safe_int(signals.get("site_count_est")) or 0
    covered = safe_int(signals.get("covered_lives_est")) or 0

    vbc = bool(signals.get("vbc_signal"))
    aco = bool(signals.get("aco_signal"))
    payer = bool(signals.get("payer_signal"))
    hs = bool(signals.get("health_system_signal"))
    idn = bool(signals.get("idn_signal"))
    enablement = bool(signals.get("enablement_signal"))
    care_mgmt = bool(signals.get("care_management_signal"))
    provider_group = bool(signals.get("provider_group_signal"))

    if subtier == "3C":
        if payer:
            return 0.90, "Payer/health plan signal present"
        return 0.0, "No payer signal"

    if subtier == "3B":
        # IDN is essentially a strong governance/network signal beyond a single hospital org.
        if idn and hs:
            return 0.92, "IDN + health system signals present"
        if idn:
            return 0.85, "IDN/network signal present"
        return 0.0, "No IDN signal"

    if subtier == "3A":
        if hs and (pcp >= thresholds.employed_pcp_floor_3a or sites >= thresholds.sites_floor_3a):
            return 0.90, "Health system signal with sufficient size"
        if hs:
            return 0.70, "Health system signal but size unclear"
        return 0.0, "No health system signal"

    if subtier == "2A":
        if aco and covered >= thresholds.covered_lives_min_2a:
            return 0.90, "ACO signal with covered lives above minimum"
        if aco and covered > 0:
            return 0.70, "ACO signal but covered lives below minimum"
        if aco:
            return 0.75, "ACO signal present but covered lives unknown"
        return 0.0, "No ACO signal"

    if subtier == "2B":
        if enablement and not provider_group and not hs and not payer:
            return 0.85, "Enablement/analytics signal without provider/payer indicators"
        if enablement:
            return 0.65, "Enablement signal present but entity type ambiguous"
        return 0.0, "No enablement signal"

    if subtier == "2C":
        if care_mgmt and not provider_group and not hs and not payer:
            return 0.85, "Care management signal without provider/payer indicators"
        if care_mgmt:
            return 0.65, "Care management signal present but entity type ambiguous"
        return 0.0, "No care management signal"

    # Provider group lanes
    if subtier == "1C":
        if vbc and pcp >= 1:
            return 0.90, "VBC participation signal with PCP presence"
        if vbc:
            return 0.70, "VBC signal present but PCP count unclear"
        return 0.0, "No VBC signal"

    if subtier == "1A":
        if provider_group and (pcp >= thresholds.pcp_floor_1a or sites >= thresholds.sites_floor_1a):
            return 0.85, "Provider group with mid-market PCP/sites"
        if provider_group:
            return 0.55, "Provider group but size unclear/too small"
        return 0.0, "No provider group signal"

    if subtier == "1B":
        if provider_group and (pcp >= thresholds.pcp_floor_1b):
            return 0.80, "PCP group with minimum PCP count"
        if provider_group:
            return 0.50, "Provider group but PCP count unclear/too small"
        return 0.0, "No provider group signal"

    return 0.0, "Unknown subtier"


def apply_precedence_rules(primary: str, scores: Dict[str, float], signals: Dict[str, Any]) -> Tuple[str, List[str], str]:
    """
    Apply precedence rules:
    - 3B overrides 3A.
    - 1C overrides 1A/1B.
    - ACO affiliation can be secondary where relevant.
    Returns (primary, secondary_tags, reason_suffix).
    """
    secondary: List[str] = []
    reason_bits: List[str] = []

    # IDN over health system
    if scores.get("3B", 0.0) >= 0.85:
        if primary != "3B":
            reason_bits.append("IDN precedence applied")
        primary = "3B"
        if scores.get("3A", 0.0) >= 0.70:
            secondary.append("3A_health_system")

    # VBC provider group overrides 1A/1B
    if scores.get("1C", 0.0) >= 0.75 and primary in {"1A", "1B"}:
        primary = "1C"
        reason_bits.append("VBC provider group precedence applied")

    # ACO affiliation as secondary tag when provider group is primary
    if primary in {"1A", "1B", "1C"} and bool(signals.get("aco_signal")):
        secondary.append("2A_aco_affiliated")
        reason_bits.append("ACO affiliation tagged secondary")

    # If payer is primary, nothing else matters much; keep a health-system secondary only if strong
    if primary == "3C" and scores.get("3A", 0.0) >= 0.85:
        secondary.append("3A_provider_owned")

    # Normalize/dedupe tags
    uniq: List[str] = []
    for t in secondary:
        if t and t not in uniq:
            uniq.append(t)

    return primary, uniq, "; ".join(reason_bits).strip()


def build_secondary_tags(primary: str, signals: Dict[str, Any]) -> List[str]:
    tags: List[str] = []
    if primary != "1C" and bool(signals.get("vbc_signal")):
        tags.append("1C_vbc_signal")
    if primary != "2A" and bool(signals.get("aco_signal")):
        tags.append("2A_aco_signal")
    if primary != "3C" and bool(signals.get("payer_signal")):
        tags.append("3C_payer_signal")
    if primary != "3A" and bool(signals.get("health_system_signal")):
        tags.append("3A_health_system_signal")
    if primary != "3B" and bool(signals.get("idn_signal")):
        tags.append("3B_idn_signal")
    if primary != "2B" and bool(signals.get("enablement_signal")):
        tags.append("2B_enablement_signal")
    if primary != "2C" and bool(signals.get("care_management_signal")):
        tags.append("2C_care_management_signal")
    uniq: List[str] = []
    for t in tags:
        if t and t not in uniq:
            uniq.append(t)
    return uniq


def apply_exclusions(row: Dict[str, Any], keywords: KeywordSignals) -> Tuple[bool, str, bool, str]:
    """
    Returns:
    - exclude_flag, exclusion_reason
    - review_flag, review_reason

    Universal exclusions rely on explicit signals; we keep "no decision-maker" as review only.
    """
    org = normalize_org_name(str(row.get("org_name") or ""))
    entity_type = str(row.get("entity_type") or "").strip().lower()

    exclusion_status = str(row.get("exclusion_status") or "").strip().lower()
    exclusion_reason = str(row.get("exclusion_reason") or "").strip()

    # Explicit flags from upstream
    if exclusion_status in {"exclude", "excluded", "disqualified"}:
        return True, (exclusion_reason or "Explicit exclusion_status from seed"), False, ""

    # Solo practitioner exclusion (account-level seed should avoid, but keep safeguard)
    if entity_type in {"individual", "solo_practitioner"}:
        return True, "Solo practitioner", False, ""

    # Telehealth-only DTC heuristic (keyword-based)
    if any(k in org for k in keywords.d2c_telehealth_keywords):
        return True, "Telehealth/DTC keyword heuristic", False, ""

    # Outside US: if primary_state missing, review (not hard exclude)
    primary_state = str(row.get("primary_state") or "").strip().upper()
    if not primary_state:
        return False, "", True, "Missing primary_state; possible outside U.S. or incomplete address"

    # No decision-maker path: do not hard exclude automatically
    return False, "", False, ""


def classify_account(
    seed_row: Dict[str, Any],
    refs: ReferenceSets,
    thresholds: Thresholds,
    keywords: KeywordSignals,
) -> Dict[str, Any]:
    """
    Compute signals, score subtiers, choose primary, apply precedence/exclusions, and output a classified row.
    """
    org_name = str(seed_row.get("org_name") or seed_row.get("org_name_raw") or "").strip()
    org_norm = normalize_org_name(org_name)
    entity_type = str(seed_row.get("entity_type") or "provider_org").strip()

    evidence_urls = str(seed_row.get("evidence_urls") or "").strip()
    evidence_notes: List[str] = []

    # Base estimates from seed
    pcp_count_est = safe_int(seed_row.get("pcp_count_est"))
    site_count_est = safe_int(seed_row.get("site_count_est"))
    covered_lives_est = safe_int(seed_row.get("covered_lives_est"))

    # Signals (boolean-ish strings + evidence notes)
    provider_group_signal = entity_type.lower() in {"provider_org", "provider_group", "practice"}
    payer_signal = False
    health_system_signal = False
    idn_signal = False
    enablement_signal = False
    care_management_signal = False
    aco_signal = False
    vbc_signal = str(seed_row.get("vbc_signal") or "").strip()
    bh_signal = str(seed_row.get("bh_signal") or "").strip()

    # Reference-based matching (best effort, exact normalized name)
    if org_norm and org_norm in refs.regional_payer_norm:
        payer_signal = True
        evidence_notes.append("Matched regional_payer_reference by name")
    if org_norm and org_norm in refs.health_system_norm:
        health_system_signal = True
        evidence_notes.append("Matched health_system_reference by name")
    if org_norm and org_norm in refs.enablement_norm:
        enablement_signal = True
        evidence_notes.append("Matched vbc_enablement_reference by name")
    if org_norm and org_norm in refs.care_management_norm:
        care_management_signal = True
        evidence_notes.append("Matched care_management_reference by name")
    if org_norm and (org_norm in refs.aco_reach_norm or org_norm in refs.mssp_aco_norm):
        aco_signal = True
        evidence_notes.append("Matched ACO reference by name")
        if not vbc_signal:
            vbc_signal = "ACO_REFERENCE_MATCH"

    # Keyword heuristics
    if any(k in org_norm for k in keywords.payer_keywords):
        payer_signal = True
        evidence_notes.append("Payer keyword heuristic")
    if any(k in org_norm for k in keywords.health_system_keywords):
        health_system_signal = True
        evidence_notes.append("Health system keyword heuristic")
    if any(k in org_norm for k in keywords.idn_keywords):
        idn_signal = True
        evidence_notes.append("IDN/network keyword heuristic")
    if any(k in org_norm for k in keywords.enablement_keywords):
        enablement_signal = True
        evidence_notes.append("Enablement keyword heuristic")
    if any(k in org_norm for k in keywords.care_mgmt_keywords):
        care_management_signal = True
        evidence_notes.append("Care management keyword heuristic")

    # Seed vbc_signal from upstream should influence aco/vbc
    if str(seed_row.get("vbc_signal") or "").strip().upper().startswith("ACO_REACH"):
        aco_signal = True
        evidence_notes.append("Seed vbc_signal indicates ACO REACH participation")

    # Size signal (best effort)
    size_bits: List[str] = []
    if pcp_count_est is not None:
        size_bits.append(f"{pcp_count_est} PCPs")
    if site_count_est is not None:
        size_bits.append(f"{site_count_est} sites")
    if covered_lives_est is not None:
        size_bits.append(f"{covered_lives_est} covered_lives")
    size_signal = ", ".join(size_bits)

    signals: Dict[str, Any] = {
        "provider_group_signal": provider_group_signal,
        "payer_signal": payer_signal,
        "health_system_signal": health_system_signal,
        "idn_signal": idn_signal,
        "enablement_signal": enablement_signal,
        "care_management_signal": care_management_signal,
        "aco_signal": aco_signal,
        "vbc_signal": vbc_signal,
        "bh_signal": bh_signal,
        "pcp_count_est": pcp_count_est,
        "site_count_est": site_count_est,
        "covered_lives_est": covered_lives_est,
    }

    # Score each subtier
    scores: Dict[str, float] = {}
    score_notes: Dict[str, str] = {}
    for st in SUBTIERS:
        s, note = score_subtier(st, signals, thresholds)
        scores[st] = float(s)
        score_notes[st] = note

    # Pick top score
    sorted_scores = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    top_st, top_score = sorted_scores[0]
    second_st, second_score = sorted_scores[1]

    # Default status
    classification_status = "classified" if top_score >= 0.75 else "unclassified"
    classification_confidence = top_score
    review_flag = False
    review_reason = ""

    # Review triggers
    if top_score < 0.50:
        review_flag = True
        review_reason = "Low confidence (<0.50) across subtiers"
    elif (top_score - second_score) <= thresholds.review_delta and top_score >= 0.50:
        review_flag = True
        review_reason = f"Close scores: {top_st}={top_score:.2f} vs {second_st}={second_score:.2f}"

    # Apply exclusions
    exclude_flag, exclusion_reason, excl_review_flag, excl_review_reason = apply_exclusions(seed_row, keywords)
    if exclude_flag:
        classification_status = "excluded"
    if excl_review_flag and not exclude_flag:
        review_flag = True
        review_reason = (review_reason + "; " if review_reason else "") + excl_review_reason

    # Apply precedence rules and build secondary tags
    primary = top_st
    primary, precedence_secondary, precedence_note = apply_precedence_rules(primary, scores, signals)

    secondary_tags = build_secondary_tags(primary, signals)
    for t in precedence_secondary:
        if t not in secondary_tags:
            secondary_tags.append(t)

    # Tier bucket is a coarse grouping for downstream sequencing
    tier_bucket = primary[0]  # "1", "2", or "3"

    # Build plain-English reason
    reason_parts: List[str] = []
    if primary in {"1A", "1B", "1C"}:
        pcp_txt = f"{pcp_count_est} PCPs" if pcp_count_est is not None else "PCP count unknown"
        if primary == "1C":
            vtxt = vbc_signal or "VBC signal"
            reason_parts.append(f"Provider group with {pcp_txt} and {vtxt}")
        elif primary == "1A":
            reason_parts.append(f"Provider group with {pcp_txt} (mid-market threshold)")
        else:
            reason_parts.append(f"PCP group with {pcp_txt} (PCP group threshold)")
        if "2A_aco_affiliated" in secondary_tags:
            reason_parts.append("ACO participation tagged secondary")
    elif primary == "2A":
        reason_parts.append("ACO entity with public ACO participation signal")
    elif primary == "2B":
        reason_parts.append("VBC enablement organization with platform/analytics signals")
    elif primary == "2C":
        reason_parts.append("Care management organization with coordination/navigation signals")
    elif primary == "3A":
        reason_parts.append("Health system with hospital/ambulatory governance signals")
    elif primary == "3B":
        reason_parts.append("IDN / network with centralized governance signals")
    elif primary == "3C":
        reason_parts.append("Regional payer / health plan with payer signals")
    else:
        reason_parts.append("Insufficient signals to classify")

    if precedence_note:
        reason_parts.append(precedence_note)

    classification_reason = "; ".join([p for p in reason_parts if p]).strip()
    if not classification_reason:
        classification_reason = f"Top score {primary}={top_score:.2f}; {score_notes.get(primary, '')}".strip()

    # Evidence notes: include top score note and any signal notes
    evidence_notes.append(f"TopScore {primary}={top_score:.2f}: {score_notes.get(primary, '')}")
    if review_flag:
        evidence_notes.append(f"ReviewTrigger: {review_reason}")

    last_verified_at = str(seed_row.get("last_verified_at") or "").strip()
    dt = parse_iso_or_none(last_verified_at)
    last_verified_at = (dt.astimezone(timezone.utc).replace(microsecond=0).isoformat() if dt else utc_now_iso())

    out: Dict[str, Any] = {
        "account_id": str(seed_row.get("account_id") or "").strip(),
        "org_name": org_name,
        "parent_org_id": str(seed_row.get("parent_org_id") or "").strip(),
        "entity_type": entity_type,
        "practice_state": str(seed_row.get("practice_state") or "").strip().upper(),
        "mailing_state": str(seed_row.get("mailing_state") or "").strip().upper(),
        "primary_state": str(seed_row.get("primary_state") or "").strip().upper(),
        "all_states_seen": str(seed_row.get("all_states_seen") or "").strip(),
        "multi_state_flag": str(seed_row.get("multi_state_flag") or "").strip().lower() in {"true", "1", "yes"} and "true" or "false",
        "subtier_primary": "" if exclude_flag else primary,
        "subtier_secondary_tags": json.dumps(secondary_tags),
        "tier_bucket": tier_bucket if not exclude_flag else "",
        "classification_confidence": f"{classification_confidence:.2f}",
        "classification_status": classification_status,
        "classification_reason": classification_reason,
        "vbc_signal": vbc_signal,
        "aco_signal": as_bool_str(aco_signal),
        "payer_signal": as_bool_str(payer_signal),
        "provider_group_signal": as_bool_str(provider_group_signal),
        "health_system_signal": as_bool_str(health_system_signal),
        "idn_signal": as_bool_str(idn_signal),
        "care_management_signal": as_bool_str(care_management_signal),
        "enablement_signal": as_bool_str(enablement_signal),
        "bh_signal": bh_signal,
        "size_signal": size_signal,
        "pcp_count_est": "" if pcp_count_est is None else str(pcp_count_est),
        "site_count_est": "" if site_count_est is None else str(site_count_est),
        "covered_lives_est": "" if covered_lives_est is None else str(covered_lives_est),
        "exclude_flag": as_bool_str(exclude_flag),
        "exclusion_reason": exclusion_reason,
        "review_flag": as_bool_str(review_flag) if not exclude_flag else "false",
        "review_reason": review_reason if not exclude_flag else "",
        "evidence_urls": evidence_urls,
        "evidence_notes": " | ".join([n for n in evidence_notes if n]),
        "last_verified_at": last_verified_at,
        "website": str(seed_row.get("website") or "").strip(),
        "phone_main": str(seed_row.get("phone_main") or "").strip(),
    }

    # Ensure exact output columns
    for col in OUTPUT_COLUMNS:
        if col not in out:
            out[col] = ""
    return {c: out.get(c, "") for c in OUTPUT_COLUMNS}


# ---------------------------
# Reference loading
# ---------------------------
def _read_csv_if_exists(path: Path) -> Optional[pd.DataFrame]:
    if not path.exists():
        return None
    try:
        return pd.read_csv(path, dtype=str).fillna("")
    except Exception as e:  # noqa: BLE001
        LOGGER.warning("Failed reading %s: %s", path, e)
        return None


def _infer_name_column(df: pd.DataFrame) -> Optional[str]:
    if df.empty:
        return None
    lower = {c.lower().strip(): c for c in df.columns}
    for key in ["org_name", "organization", "organization_name", "name", "legal_name", "entity_name", "participant_name"]:
        if key in lower:
            return lower[key]
    for c in df.columns:
        if "name" in c.lower():
            return c
    return None


def load_reference_sets(base_dir: Path) -> ReferenceSets:
    """
    Load optional reference files from /input or /output under base_dir.
    """
    input_dir = base_dir / "input"
    output_dir = base_dir / "output"

    def load_list(filename: str) -> Tuple[Tuple[str, ...], frozenset[str]]:
        for p in [input_dir / filename, output_dir / filename]:
            df = _read_csv_if_exists(p)
            if df is None:
                continue
            name_col = _infer_name_column(df)
            if not name_col:
                continue
            names = [str(x).strip() for x in df[name_col].astype(str).tolist() if str(x).strip()]
            norm = frozenset(normalize_org_name(n) for n in names if normalize_org_name(n))
            return tuple(names), norm
        return tuple(), frozenset()

    reach_names, reach_norm = load_list("cms_aco_reach_participants.csv")
    mssp_names, mssp_norm = load_list("cms_mssp_aco_reference.csv")
    hs_names, hs_norm = load_list("health_system_reference.csv")
    payer_names, payer_norm = load_list("regional_payer_reference.csv")
    enable_names, enable_norm = load_list("vbc_enablement_reference.csv")
    cm_names, cm_norm = load_list("care_management_reference.csv")

    return ReferenceSets(
        aco_reach_names=reach_names,
        mssp_aco_names=mssp_names,
        health_system_names=hs_names,
        regional_payer_names=payer_names,
        enablement_names=enable_names,
        care_management_names=cm_names,
        aco_reach_norm=reach_norm,
        mssp_aco_norm=mssp_norm,
        health_system_norm=hs_norm,
        regional_payer_norm=payer_norm,
        enablement_norm=enable_norm,
        care_management_norm=cm_norm,
    )


def ensure_output_dirs(output_dir: Path) -> Path:
    out = output_dir / "output"
    out.mkdir(parents=True, exist_ok=True)
    return out


def read_seed_file(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")
    return df


def write_csv(path: Path, df: pd.DataFrame, columns: List[str]) -> None:
    for c in columns:
        if c not in df.columns:
            df[c] = ""
    df[columns].to_csv(path, index=False)


def build_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["primary_state", "subtier_primary", "count"])
    tmp = df.copy()
    tmp["primary_state"] = tmp["primary_state"].astype(str).str.upper()
    tmp["subtier_primary"] = tmp["subtier_primary"].astype(str)
    grouped = tmp.groupby(["primary_state", "subtier_primary"], dropna=False).size().reset_index(name="count")
    return grouped.sort_values(["primary_state", "subtier_primary"])


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Classify seeded accounts into Kivira 9-subtier architecture.")
    p.add_argument("--base-dir", default=".", help="Repo/base directory containing output/ and optional input/.")
    p.add_argument("--states", default="GA,NC", help="Comma-separated list of seed states to process.")
    p.add_argument("--log-level", default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR).")
    args = p.parse_args(argv)

    logging.basicConfig(level=getattr(logging, str(args.log_level).upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s - %(message)s")

    base_dir = Path(args.base_dir).expanduser().resolve()
    out_dir = ensure_output_dirs(base_dir)

    thresholds = Thresholds()
    keywords = KeywordSignals()
    refs = load_reference_sets(base_dir)

    states = [s.strip().upper() for s in str(args.states).split(",") if s.strip()]
    seed_paths: List[Tuple[str, Path]] = []
    for st in states:
        seed_paths.append((st, base_dir / "output" / f"accounts_seed_{st}.csv"))

    all_classified_rows: List[Dict[str, Any]] = []
    review_rows: List[Dict[str, Any]] = []
    exclusion_rows: List[Dict[str, Any]] = []

    for st, seed_path in seed_paths:
        if not seed_path.exists():
            LOGGER.warning("Missing seed file: %s (skipping)", seed_path)
            continue
        LOGGER.info("Classifying seed file for %s: %s", st, seed_path)
        seed_df = read_seed_file(seed_path)
        classified = [classify_account(r._asdict() if hasattr(r, "_asdict") else dict(r), refs, thresholds, keywords) for r in seed_df.to_dict(orient="records")]
        classified_df = pd.DataFrame(classified)
        write_csv(out_dir / f"accounts_classified_{st}.csv", classified_df, OUTPUT_COLUMNS)

        all_classified_rows.extend(classified)

    all_df = pd.DataFrame(all_classified_rows)
    if all_df.empty:
        # Still write empty outputs (idempotent)
        write_csv(out_dir / "accounts_classified_all.csv", all_df, OUTPUT_COLUMNS)
        write_csv(out_dir / "classification_review_queue.csv", pd.DataFrame(), OUTPUT_COLUMNS)
        write_csv(out_dir / "classification_exclusions.csv", pd.DataFrame(), OUTPUT_COLUMNS)
        (out_dir / "subtier_summary_by_state.csv").write_text("primary_state,subtier_primary,count\n", encoding="utf-8")
        return 0

    # Split review & exclusions
    all_df["exclude_flag"] = all_df["exclude_flag"].astype(str).str.lower()
    all_df["review_flag"] = all_df["review_flag"].astype(str).str.lower()
    excl_df = all_df[all_df["exclude_flag"] == "true"].copy()
    rev_df = all_df[(all_df["exclude_flag"] != "true") & (all_df["review_flag"] == "true")].copy()

    write_csv(out_dir / "accounts_classified_all.csv", all_df, OUTPUT_COLUMNS)
    write_csv(out_dir / "classification_review_queue.csv", rev_df, OUTPUT_COLUMNS)
    write_csv(out_dir / "classification_exclusions.csv", excl_df, OUTPUT_COLUMNS)

    summary = build_summary(all_df[all_df["exclude_flag"] != "true"].copy())
    summary.to_csv(out_dir / "subtier_summary_by_state.csv", index=False)

    LOGGER.info("Done. Classified=%s Review=%s Excluded=%s", len(all_df), len(rev_df), len(excl_df))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

