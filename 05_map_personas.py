#!/usr/bin/env python3
"""
05_map_personas.py

Map extracted public contacts to Kivira buying-committee personas by subtier using
deterministic title dictionaries + confidence scoring.

Inputs (defaults under ./output/):
- output/contacts_raw_GA.csv
- output/contacts_raw_NC.csv
- output/accounts_classified_GA.csv
- output/accounts_classified_NC.csv
- optional config/persona_title_dictionary.json
- optional config/title_normalization_overrides.json

Outputs (under output_dir/output/):
- contacts_mapped_GA.csv
- contacts_mapped_NC.csv
- contacts_mapped_all.csv
- persona_review_queue.csv
- account_buying_committee_summary.csv
- persona_mapping_errors.csv

Dependencies: pandas, rapidfuzz (optional fallback), python-dateutil, standard library.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd
from dateutil.parser import isoparse

from tam_builder.pilot_filters import resolve_output_dir

try:
    from rapidfuzz import fuzz as _rapidfuzz_fuzz  # type: ignore
except Exception:  # noqa: BLE001
    _rapidfuzz_fuzz = None


LOGGER = logging.getLogger("kivira.personas")


ROLE_OPERATIONAL_OWNER = "Operational Owner"
ROLE_CLINICAL_CHAMPION = "Clinical Champion"
ROLE_ECONOMIC_BUYER = "Economic Buyer"
ROLE_TECH_GATEKEEPER = "Technical Gatekeeper"
ROLE_BH_QUALITY = "BH / Quality Influencer"

ROLE_ORDER: List[str] = [
    ROLE_OPERATIONAL_OWNER,
    ROLE_CLINICAL_CHAMPION,
    ROLE_ECONOMIC_BUYER,
    ROLE_TECH_GATEKEEPER,
    ROLE_BH_QUALITY,
]


OUTPUT_COLUMNS: List[str] = [
    "contact_id",
    "account_id",
    "org_name",
    "parent_org_id",
    "primary_state",
    "subtier_primary",
    "subtier_secondary_tags",
    "person_name",
    "first_name",
    "last_name",
    "job_title",
    "title_normalized",
    "department",
    "seniority_guess",
    "persona_role_primary",
    "persona_role_secondary",
    "role_priority_rank",
    "outreach_sequence_stage",
    "demo_bookable_flag",
    "buying_committee_fit_score",
    "role_match_confidence",
    "title_match_method",
    "title_match_rule",
    "economic_buyer_flag",
    "clinical_champion_flag",
    "operational_owner_flag",
    "technical_gatekeeper_flag",
    "bh_quality_influencer_flag",
    "wave_1_eligible_flag",
    "review_flag",
    "review_reason",
    "source_url",
    "linkedin_profile_url",
    "email",
    "phone_direct",
    "phone_main",
    "evidence_notes",
    "last_verified_at",
]


SUMMARY_COLUMNS: List[str] = [
    "account_id",
    "org_name",
    "subtier_primary",
    "primary_state",
    "contact_1_name",
    "contact_1_role",
    "contact_1_score",
    "contact_2_name",
    "contact_2_role",
    "contact_2_score",
    "economic_buyer_name",
    "economic_buyer_role",
    "economic_buyer_score",
    "technical_gatekeeper_name",
    "technical_gatekeeper_role",
    "technical_gatekeeper_score",
    "bh_quality_name",
    "bh_quality_role",
    "bh_quality_score",
    "committee_coverage_score",
    "committee_gap_notes",
    "last_verified_at",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_iso_or_now(value: Any) -> str:
    s = str(value or "").strip()
    if not s:
        return utc_now_iso()
    try:
        dt = isoparse(s)
        return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()
    except Exception:
        return utc_now_iso()


def token_sort_ratio(a: str, b: str) -> int:
    a = (a or "").strip()
    b = (b or "").strip()
    if not a and not b:
        return 100
    if _rapidfuzz_fuzz is not None:
        return int(_rapidfuzz_fuzz.token_sort_ratio(a, b))
    import difflib

    def norm_tokens(s: str) -> str:
        toks = [t for t in re.split(r"\s+", s.upper()) if t]
        toks.sort()
        return " ".join(toks)

    return int(round(difflib.SequenceMatcher(a=norm_tokens(a), b=norm_tokens(b)).ratio() * 100))


# ---------------------------
# Configurable dictionaries
# ---------------------------
DEFAULT_ABBREVIATIONS: Dict[str, str] = {
    "CMO": "Chief Medical Officer",
    "COO": "Chief Operating Officer",
    "CEO": "Chief Executive Officer",
    "CFO": "Chief Financial Officer",
    "CIO": "Chief Information Officer",
    "CTO": "Chief Technology Officer",
    "CMIO": "Chief Medical Information Officer",
    "VP POP HEALTH": "VP Population Health",
    "DIR CARE MGMT": "Director of Care Management",
}


def normalize_title(title: str, overrides: Dict[str, str] | None = None) -> str:
    t = " ".join((title or "").split())
    if not t:
        return ""
    overrides = overrides or {}
    for k, v in overrides.items():
        if t.strip().lower() == str(k).strip().lower():
            return str(v).strip()
    # minimal normalization of separators
    t2 = re.sub(r"\s*[,/|]\s*", " ", t)
    t2 = re.sub(r"\s+", " ", t2).strip()
    # common expansions
    if t2.strip().upper() in DEFAULT_ABBREVIATIONS:
        return DEFAULT_ABBREVIATIONS[t2.strip().upper()]
    t2 = re.sub(r"(?i)\bVP\s+Pop\s+Health\b", "VP Population Health", t2)
    t2 = re.sub(r"(?i)\bDir(?:ector)?\s+Care\s+Mgmt\b", "Director of Care Management", t2)
    return t2


def expand_abbreviations(title_norm: str, abbreviations: Dict[str, str] | None = None) -> Tuple[str, bool]:
    """
    Expand abbreviations within a normalized title (best effort).
    Returns (expanded_title, changed_flag).
    """
    abbreviations = abbreviations or DEFAULT_ABBREVIATIONS
    t = (title_norm or "").strip()
    if not t:
        return "", False
    key = t.upper()
    if key in abbreviations:
        return abbreviations[key], True
    # Replace common standalone abbreviations
    changed = False
    out = t
    for k, v in abbreviations.items():
        # match whole-word (case-insensitive)
        pattern = r"(?i)\b" + re.escape(k) + r"\b"
        if re.search(pattern, out):
            out = re.sub(pattern, v, out)
            changed = True
    out = " ".join(out.split())
    return out, changed


def default_title_dictionary() -> Dict[str, Dict[str, List[str]]]:
    """
    Default subtier -> role -> list of title variants.
    This is intentionally compact; prefer providing config/persona_title_dictionary.json for full coverage.
    """
    # Shared across provider org lanes
    operational = [
        "Director of Operations",
        "VP Operations",
        "Clinical Operations Director",
        "Practice Administrator",
        "Practice Manager",
        "Director of Care Management",
        "Population Health Director",
        "Director of Quality",
    ]
    clinical = [
        "Chief Medical Officer",
        "Medical Director",
        "Primary Care Medical Director",
        "VP Medical Affairs",
        "Associate Medical Director",
    ]
    economic = [
        "Chief Executive Officer",
        "Chief Operating Officer",
        "Chief Financial Officer",
        "President",
        "Owner",
        "Managing Partner",
    ]
    technical = [
        "Chief Medical Information Officer",
        "IT Director",
        "Director of Health IT",
        "EHR Administrator",
        "Director of Clinical Informatics",
        "VP Integrations",
        "Director of Analytics",
        "Chief Information Officer",
    ]
    bhq = [
        "Director of Behavioral Health",
        "Behavioral Health Program Director",
        "BH Integration Director",
        "Director of Quality Improvement",
        "VP Quality",
        "Director of HEDIS",
        "Quality Program Manager",
    ]

    def pack() -> Dict[str, List[str]]:
        return {
            ROLE_OPERATIONAL_OWNER: operational,
            ROLE_CLINICAL_CHAMPION: clinical,
            ROLE_ECONOMIC_BUYER: economic,
            ROLE_TECH_GATEKEEPER: technical,
            ROLE_BH_QUALITY: bhq,
        }

    # For enablement/payers: emphasize product/partnership/quality titles
    enablement_op = [
        "Head of Partnerships",
        "VP Partnerships",
        "Head of Product",
        "VP Product",
        "Chief Product Officer",
        "VP Engineering",
        "VP Integrations",
        "Director of Implementation",
    ]
    payer_quality = [
        "VP Quality",
        "Director of Quality",
        "Director of Stars",
        "HEDIS Director",
        "Medical Director",
        "Chief Medical Officer",
        "VP Medical Management",
    ]

    d: Dict[str, Dict[str, List[str]]] = {}
    for st in ["1A", "1B", "1C", "2A", "3A", "3B"]:
        d[st] = pack()
    d["2B"] = {
        ROLE_OPERATIONAL_OWNER: ["COO", "Chief Operating Officer", "VP Operations", "Director of Operations", "Head of Implementation", "VP Customer Success"],
        ROLE_CLINICAL_CHAMPION: ["Chief Medical Officer", "Medical Director", "Chief Clinical Officer"],
        ROLE_ECONOMIC_BUYER: ["Chief Executive Officer", "CEO", "President", "CFO"],
        ROLE_TECH_GATEKEEPER: ["CTO", "Chief Technology Officer", "VP Engineering", "Head of Engineering", "VP Integrations", "Director of Security", "CIO"],
        ROLE_BH_QUALITY: ["VP Quality", "Director of Quality", "Clinical Quality Director"],
    }
    d["2C"] = {
        ROLE_OPERATIONAL_OWNER: ["Director of Care Management", "VP Clinical Operations", "Director of Operations", "VP Operations"],
        ROLE_CLINICAL_CHAMPION: ["Medical Director", "Chief Medical Officer", "Clinical Director"],
        ROLE_ECONOMIC_BUYER: ["CEO", "Chief Executive Officer", "President", "COO"],
        ROLE_TECH_GATEKEEPER: ["IT Director", "CIO", "Director of Analytics", "VP Integrations"],
        ROLE_BH_QUALITY: ["Director of Behavioral Health", "Director of Quality", "VP Quality"],
    }
    d["3C"] = {
        ROLE_OPERATIONAL_OWNER: ["VP Operations", "Director of Operations", "VP Population Health", "Director of Population Health"],
        ROLE_CLINICAL_CHAMPION: ["Chief Medical Officer", "Medical Director", "VP Medical Management"],
        ROLE_ECONOMIC_BUYER: ["CEO", "President", "COO", "CFO"],
        ROLE_TECH_GATEKEEPER: ["CIO", "CTO", "VP Engineering", "Director of Analytics", "VP Integrations"],
        ROLE_BH_QUALITY: payer_quality,
    }
    return d


def load_json_if_exists(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        LOGGER.warning("Failed reading JSON %s: %s", path, e)
        return None


def load_title_dictionary(base_dir: Path) -> Dict[str, Dict[str, List[str]]]:
    cfg_path = base_dir / "config" / "persona_title_dictionary.json"
    data = load_json_if_exists(cfg_path)
    if not data:
        return default_title_dictionary()
    # Expect: { "1A": { "Operational Owner": ["..."], ... }, ... }
    out: Dict[str, Dict[str, List[str]]] = {}
    for st, roles in data.items():
        if not isinstance(roles, dict):
            continue
        out[st.strip().upper()] = {}
        for role, titles in roles.items():
            if not isinstance(titles, list):
                continue
            out[st.strip().upper()][str(role)] = [str(t).strip() for t in titles if str(t).strip()]
    return out or default_title_dictionary()


def load_title_overrides(base_dir: Path) -> Dict[str, str]:
    cfg_path = base_dir / "config" / "title_normalization_overrides.json"
    data = load_json_if_exists(cfg_path)
    if not data or not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items()}


# ---------------------------
# Matching + scoring
# ---------------------------
@dataclass(frozen=True)
class Weights:
    role_title_fit: float = 0.40
    subtier_alignment: float = 0.20
    seniority: float = 0.15
    department: float = 0.10
    contactability: float = 0.10
    source_quality: float = 0.05


def _seniority_relevance(role: str, seniority_guess: str) -> float:
    s = (seniority_guess or "").lower()
    if not s:
        return 0.0
    if role == ROLE_ECONOMIC_BUYER:
        return 1.0 if s in {"executive", "vp"} else 0.4
    if role == ROLE_TECH_GATEKEEPER:
        return 1.0 if s in {"technical", "executive", "vp", "director"} else 0.3
    if role == ROLE_CLINICAL_CHAMPION:
        return 1.0 if s in {"executive", "physician_leader", "director"} else 0.4
    if role == ROLE_OPERATIONAL_OWNER:
        return 1.0 if s in {"director", "manager", "vp", "admin"} else 0.4
    if role == ROLE_BH_QUALITY:
        return 1.0 if s in {"director", "manager", "vp", "physician_leader"} else 0.4
    return 0.0


def _department_relevance(role: str, title_norm: str, department: str) -> float:
    text = " ".join([title_norm or "", department or ""]).lower()
    if role == ROLE_TECH_GATEKEEPER:
        return 1.0 if any(k in text for k in ["it", "informatics", "security", "analytics", "integration", "ehr", "technology"]) else 0.2
    if role == ROLE_OPERATIONAL_OWNER:
        return 1.0 if any(k in text for k in ["operations", "care management", "population health", "quality", "clinical operations"]) else 0.3
    if role == ROLE_CLINICAL_CHAMPION:
        return 1.0 if any(k in text for k in ["medical", "clinical", "primary care", "physician"]) else 0.3
    if role == ROLE_BH_QUALITY:
        return 1.0 if any(k in text for k in ["behavioral", "mental", "quality", "hedis", "stars"]) else 0.3
    if role == ROLE_ECONOMIC_BUYER:
        return 1.0 if any(k in text for k in ["ceo", "coo", "cfo", "president", "owner", "partner"]) else 0.4
    return 0.0


def score_role_match(
    *,
    subtier: str,
    role: str,
    job_title_raw: str,
    title_norm: str,
    title_dict: Dict[str, Dict[str, List[str]]],
    seniority_guess: str,
    department: str,
    has_email: bool,
    has_phone: bool,
    source_page_priority: Any,
    weights: Weights,
) -> Tuple[float, float, str, str]:
    """
    Returns (role_match_confidence, buying_committee_fit_score, match_method, match_rule)
    """
    st = (subtier or "").strip().upper()
    role_titles = title_dict.get(st, {}).get(role, [])

    # Base match confidence from title matching.
    match_method = "rule_inference"
    match_rule = "no_dictionary_match"
    role_conf = 0.0

    title_norm2 = title_norm.strip()
    expanded, changed = expand_abbreviations(title_norm2)

    # Exact / normalized exact
    for t in role_titles:
        if not t:
            continue
        if job_title_raw.strip().lower() == t.strip().lower():
            role_conf = 0.95
            match_method = "exact"
            match_rule = f"exact:{t}"
            break
        if title_norm2.lower() == t.strip().lower():
            role_conf = max(role_conf, 0.90)
            match_method = "normalized_exact"
            match_rule = f"normalized_exact:{t}"
        if changed and expanded.lower() == t.strip().lower():
            role_conf = max(role_conf, 0.88)
            match_method = "abbreviation_expansion"
            match_rule = f"abbrev:{t}"

    # Fuzzy fallback
    if role_conf < 0.80 and role_titles and (title_norm2 or expanded):
        best = 0
        best_t = ""
        for t in role_titles:
            s = token_sort_ratio(expanded or title_norm2, t)
            if s > best:
                best = s
                best_t = t
        if best >= 92:
            role_conf = max(role_conf, 0.85)
            match_method = "fuzzy"
            match_rule = f"fuzzy:{best_t}:{best}"
        elif best >= 85:
            role_conf = max(role_conf, 0.75)
            match_method = "fuzzy"
            match_rule = f"fuzzy_weak:{best_t}:{best}"

    # Role/title fit score (0..1)
    role_title_fit = role_conf

    subtier_alignment = 1.0 if st in title_dict else 0.6
    seniority_rel = _seniority_relevance(role, seniority_guess)
    dept_rel = _department_relevance(role, expanded or title_norm2, department)
    contactability = (1.0 if has_email else 0.0) * 0.6 + (1.0 if has_phone else 0.0) * 0.4

    # Source quality: low weight; prioritize top pages
    try:
        pri = int(str(source_page_priority))
    except Exception:
        pri = 5
    source_quality = 1.0 if pri == 1 else 0.7 if pri == 2 else 0.4

    fit = (
        weights.role_title_fit * role_title_fit
        + weights.subtier_alignment * subtier_alignment
        + weights.seniority * seniority_rel
        + weights.department * dept_rel
        + weights.contactability * contactability
        + weights.source_quality * source_quality
    )
    fit = max(0.0, min(1.0, fit))

    return role_conf, fit, match_method, match_rule


def map_contact_to_roles(
    contact: Dict[str, Any],
    title_dict: Dict[str, Dict[str, List[str]]],
    overrides: Dict[str, str],
    weights: Weights,
    demo_bookable_min_fit: float = 0.60,
) -> Dict[str, Any]:
    """
    Returns output row with role fields populated.
    """
    subtier = str(contact.get("subtier_primary") or "").strip().upper()
    job_title = str(contact.get("job_title") or "").strip()
    title_norm = normalize_title(str(contact.get("title_normalized") or job_title), overrides)
    dept = str(contact.get("department") or "").strip()
    seniority_guess = str(contact.get("seniority_guess") or "").strip()

    has_email = bool(str(contact.get("email") or "").strip())
    has_phone = bool(str(contact.get("phone_direct") or "").strip() or str(contact.get("phone_main") or "").strip())
    source_page_priority = contact.get("source_page_priority")

    role_scores: List[Tuple[str, float, float, str, str]] = []
    for role in ROLE_ORDER:
        role_conf, fit, method, rule = score_role_match(
            subtier=subtier,
            role=role,
            job_title_raw=job_title,
            title_norm=title_norm,
            title_dict=title_dict,
            seniority_guess=seniority_guess,
            department=dept,
            has_email=has_email,
            has_phone=has_phone,
            source_page_priority=source_page_priority,
            weights=weights,
        )
        role_scores.append((role, fit, role_conf, method, rule))

    role_scores.sort(key=lambda x: x[1], reverse=True)
    best_role, best_fit, best_conf, best_method, best_rule = role_scores[0]
    second_role, second_fit, _, _, _ = role_scores[1]

    # Multi-role assignment when close and both plausible.
    primary = best_role if best_fit >= 0.55 else ""
    secondary = ""
    if primary and (second_fit >= 0.55) and (best_fit - second_fit) <= 0.12:
        secondary = second_role

    # Tier 1B: physician owner / partner can be dual role.
    if subtier == "1B" and primary:
        t = (title_norm or job_title).lower()
        if any(k in t for k in ["owner", "partner", "physician owner", "managing partner"]):
            if primary != ROLE_ECONOMIC_BUYER:
                secondary = ROLE_ECONOMIC_BUYER if secondary != ROLE_ECONOMIC_BUYER else secondary

    # Outreach stage mapping
    stage = "parallel"
    if primary == ROLE_OPERATIONAL_OWNER:
        stage = "first"
    elif primary == ROLE_CLINICAL_CHAMPION:
        stage = "second"
    elif primary == ROLE_ECONOMIC_BUYER:
        stage = "third"
    elif primary == ROLE_TECH_GATEKEEPER:
        stage = "parallel"
    elif primary == ROLE_BH_QUALITY:
        stage = "demo_stage"

    min_fit = float(demo_bookable_min_fit)
    demo_bookable = bool(primary) and best_fit >= min_fit
    # Filter out obvious non-demo targets
    if any(k in (title_norm or job_title).lower() for k in ["media", "press", "investor relations", "careers", "recruit"]):
        demo_bookable = False

    review_flag = False
    review_reasons: List[str] = []
    if not primary and (job_title or title_norm):
        review_flag = True
        review_reasons.append("no_strong_role_fit")
    if primary and not job_title:
        review_flag = True
        review_reasons.append("missing_job_title")
    if primary and secondary and abs(best_fit - second_fit) <= 0.05:
        review_flag = True
        review_reasons.append("roles_too_close")
    if primary and best_fit < 0.65 and seniority_guess in {"executive", "vp"}:
        review_flag = True
        review_reasons.append("high_seniority_low_role_fit")

    # Evidence notes
    note = ""
    if primary:
        note = f"Mapped to {primary} because title match ({best_method}) for subtier {subtier}: {best_rule}"
        if secondary:
            note += f"; secondary role {secondary} due to close score"
    else:
        note = "No strong persona match from title dictionary; review needed"

    out = dict(contact)
    out["persona_role_primary"] = primary
    out["persona_role_secondary"] = secondary
    out["outreach_sequence_stage"] = stage if primary else ""
    out["demo_bookable_flag"] = "true" if demo_bookable else "false"
    out["buying_committee_fit_score"] = f"{best_fit:.2f}"
    out["role_match_confidence"] = f"{best_conf:.2f}"
    out["title_match_method"] = best_method
    out["title_match_rule"] = best_rule

    out["economic_buyer_flag"] = "true" if primary == ROLE_ECONOMIC_BUYER or secondary == ROLE_ECONOMIC_BUYER else "false"
    out["clinical_champion_flag"] = "true" if primary == ROLE_CLINICAL_CHAMPION or secondary == ROLE_CLINICAL_CHAMPION else "false"
    out["operational_owner_flag"] = "true" if primary == ROLE_OPERATIONAL_OWNER or secondary == ROLE_OPERATIONAL_OWNER else "false"
    out["technical_gatekeeper_flag"] = "true" if primary == ROLE_TECH_GATEKEEPER or secondary == ROLE_TECH_GATEKEEPER else "false"
    out["bh_quality_influencer_flag"] = "true" if primary == ROLE_BH_QUALITY or secondary == ROLE_BH_QUALITY else "false"

    out["review_flag"] = "true" if review_flag else "false"
    out["review_reason"] = ";".join(review_reasons)
    out["evidence_notes"] = _merge_notes(str(contact.get("evidence_notes") or "").strip(), note)
    out["last_verified_at"] = parse_iso_or_now(out.get("last_verified_at"))

    # Defaults; filled later
    out["role_priority_rank"] = ""
    out["wave_1_eligible_flag"] = "false"

    # Ensure schema
    for c in OUTPUT_COLUMNS:
        if c not in out:
            out[c] = ""
        if out[c] is None:
            out[c] = ""
        if not isinstance(out[c], str):
            out[c] = str(out[c])
    return {c: out.get(c, "") for c in OUTPUT_COLUMNS}


def _merge_notes(a: str, b: str) -> str:
    a = (a or "").strip()
    b = (b or "").strip()
    if not a:
        return b
    if not b:
        return a
    if b in a:
        return a
    return a + " | " + b


def rank_contacts_within_account(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Assign role_priority_rank (1..5) based on best contact per role.
    Also set wave_1_eligible_flag for the top Operational Owner (and sometimes Clinical Champion for small practices).
    """
    # Sort by fit score descending
    def fit(r: Dict[str, Any]) -> float:
        try:
            return float(str(r.get("buying_committee_fit_score") or "0"))
        except Exception:
            return 0.0

    rows_sorted = sorted(rows, key=fit, reverse=True)

    best_by_role: Dict[str, Dict[str, Any]] = {}
    for r in rows_sorted:
        role = str(r.get("persona_role_primary") or "")
        if not role:
            continue
        if role not in best_by_role:
            best_by_role[role] = r

    # Assign role_priority_rank based on fixed role order
    for i, role in enumerate(ROLE_ORDER, start=1):
        best = best_by_role.get(role)
        if not best:
            continue
        # Mark the best instance
        for r in rows:
            if r.get("contact_id") == best.get("contact_id") and r.get("persona_role_primary") == role:
                r["role_priority_rank"] = str(i)

    # Wave 1: Operational Owner best; plus Clinical Champion sometimes if close or no operator.
    op = best_by_role.get(ROLE_OPERATIONAL_OWNER)
    cc = best_by_role.get(ROLE_CLINICAL_CHAMPION)
    if op:
        op["wave_1_eligible_flag"] = "true"
    else:
        # if no operator, allow best clinical champion as wave 1
        if cc:
            cc["wave_1_eligible_flag"] = "true"

    if op and cc:
        # If co-equal in score, allow both
        if abs(fit(op) - fit(cc)) <= 0.08:
            cc["wave_1_eligible_flag"] = "true"

    return rows


def build_account_committee_summary(mapped_df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per account with top contacts and coverage.
    """
    if mapped_df.empty:
        return pd.DataFrame(columns=SUMMARY_COLUMNS)

    def fit(r: pd.Series) -> float:
        try:
            return float(str(r.get("buying_committee_fit_score") or "0"))
        except Exception:
            return 0.0

    summaries: List[Dict[str, Any]] = []
    for account_id, g in mapped_df.groupby("account_id", dropna=False):
        g2 = g.copy()
        g2["fit_num"] = g2.apply(fit, axis=1)
        g2 = g2.sort_values("fit_num", ascending=False)

        org_name = str(g2["org_name"].iloc[0]) if "org_name" in g2.columns and len(g2) else ""
        subtier = str(g2["subtier_primary"].iloc[0]) if "subtier_primary" in g2.columns and len(g2) else ""
        state = str(g2["primary_state"].iloc[0]) if "primary_state" in g2.columns and len(g2) else ""
        last_verified_at = parse_iso_or_now(g2["last_verified_at"].iloc[0] if "last_verified_at" in g2.columns and len(g2) else "")

        top = g2[g2["persona_role_primary"].astype(str) != ""].head(2)
        c1_name = str(top["person_name"].iloc[0]) if len(top) >= 1 else ""
        c1_role = str(top["persona_role_primary"].iloc[0]) if len(top) >= 1 else ""
        c1_score = str(top["buying_committee_fit_score"].iloc[0]) if len(top) >= 1 else ""
        c2_name = str(top["person_name"].iloc[1]) if len(top) >= 2 else ""
        c2_role = str(top["persona_role_primary"].iloc[1]) if len(top) >= 2 else ""
        c2_score = str(top["buying_committee_fit_score"].iloc[1]) if len(top) >= 2 else ""

        def best_for(role: str) -> Tuple[str, str, str]:
            gg = g2[g2["persona_role_primary"].astype(str) == role]
            if gg.empty:
                return "", "", ""
            rr = gg.iloc[0]
            return str(rr.get("person_name") or ""), str(rr.get("persona_role_primary") or ""), str(rr.get("buying_committee_fit_score") or "")

        eb_name, eb_role, eb_score = best_for(ROLE_ECONOMIC_BUYER)
        tg_name, tg_role, tg_score = best_for(ROLE_TECH_GATEKEEPER)
        bq_name, bq_role, bq_score = best_for(ROLE_BH_QUALITY)

        present_roles = set(r for r in g2["persona_role_primary"].astype(str).tolist() if r)
        coverage = len(present_roles.intersection(set(ROLE_ORDER))) / float(len(ROLE_ORDER))
        gap_roles = [r for r in ROLE_ORDER if r not in present_roles]
        gap_notes = "Missing: " + ", ".join(gap_roles) if gap_roles else "Full committee coverage"

        summaries.append(
            {
                "account_id": str(account_id),
                "org_name": org_name,
                "subtier_primary": subtier,
                "primary_state": state,
                "contact_1_name": c1_name,
                "contact_1_role": c1_role,
                "contact_1_score": c1_score,
                "contact_2_name": c2_name,
                "contact_2_role": c2_role,
                "contact_2_score": c2_score,
                "economic_buyer_name": eb_name,
                "economic_buyer_role": eb_role,
                "economic_buyer_score": eb_score,
                "technical_gatekeeper_name": tg_name,
                "technical_gatekeeper_role": tg_role,
                "technical_gatekeeper_score": tg_score,
                "bh_quality_name": bq_name,
                "bh_quality_role": bq_role,
                "bh_quality_score": bq_score,
                "committee_coverage_score": f"{coverage:.2f}",
                "committee_gap_notes": gap_notes,
                "last_verified_at": last_verified_at,
            }
        )

    df = pd.DataFrame(summaries)
    for c in SUMMARY_COLUMNS:
        if c not in df.columns:
            df[c] = ""
    return df[SUMMARY_COLUMNS]


# ---------------------------
# IO pipeline
# ---------------------------
def read_csv_safe(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str).fillna("")


def write_csv(path: Path, df: pd.DataFrame, columns: List[str]) -> None:
    for c in columns:
        if c not in df.columns:
            df[c] = ""
    df[columns].to_csv(path, index=False)


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Map contacts to buying-committee personas by subtier.")
    p.add_argument("--base-dir", default=".", help="Base directory containing output/ and optional config/.")
    p.add_argument("--states", default="GA,NC", help="Comma-separated states to process (default GA,NC).")
    p.add_argument("--log-level", default="INFO", help="Logging level.")
    p.add_argument(
        "--output-subdir",
        default="",
        help="Read/write under output/<subdir>/ (e.g. pilot).",
    )
    p.add_argument(
        "--demo-bookable-min-fit",
        type=float,
        default=0.60,
        help="Minimum buying_committee_fit_score for demo_bookable_flag (pilot: try 0.55).",
    )
    args = p.parse_args(argv)

    logging.basicConfig(level=getattr(logging, str(args.log_level).upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s - %(message)s")

    base_dir = Path(args.base_dir).expanduser().resolve()
    out_dir = resolve_output_dir(base_dir, str(args.output_subdir or ""))

    title_dict = load_title_dictionary(base_dir)
    overrides = load_title_overrides(base_dir)
    weights = Weights()

    states = [s.strip().upper() for s in str(args.states).split(",") if s.strip()]

    all_rows: List[Dict[str, Any]] = []
    all_errors: List[Dict[str, Any]] = []

    for st in states:
        contacts_path = out_dir / f"contacts_raw_{st}.csv"
        classified_path = out_dir / f"accounts_classified_{st}.csv"
        if not contacts_path.exists() or not classified_path.exists():
            LOGGER.warning("Missing inputs for %s (skipping): %s %s", st, contacts_path, classified_path)
            continue

        LOGGER.info("Persona mapping for %s", st)
        contacts_df = read_csv_safe(contacts_path)
        classified_df = read_csv_safe(classified_path)

        acct_idx: Dict[str, Dict[str, Any]] = {str(r.get("account_id") or "").strip(): r for r in classified_df.to_dict(orient="records") if str(r.get("account_id") or "").strip()}

        mapped_rows: List[Dict[str, Any]] = []
        for r in contacts_df.to_dict(orient="records"):
            try:
                account_id = str(r.get("account_id") or "").strip()
                acct = acct_idx.get(account_id, {})
                merged = dict(r)
                # Ensure key fields (contacts_raw already has most, but keep consistent)
                for k in ["org_name", "parent_org_id", "primary_state", "subtier_primary", "subtier_secondary_tags"]:
                    if not merged.get(k):
                        merged[k] = acct.get(k, "")
                # Ensure title fields
                merged["title_normalized"] = normalize_title(str(merged.get("title_normalized") or merged.get("job_title") or ""), overrides)
                mapped = map_contact_to_roles(
                    merged,
                    title_dict,
                    overrides,
                    weights,
                    demo_bookable_min_fit=float(args.demo_bookable_min_fit),
                )
                mapped_rows.append(mapped)
            except Exception as e:  # noqa: BLE001
                all_errors.append({"state": st, "contact_id": r.get("contact_id", ""), "account_id": r.get("account_id", ""), "error": str(e), "at": utc_now_iso()})

        # Rank within account
        by_acct: Dict[str, List[Dict[str, Any]]] = {}
        for mr in mapped_rows:
            by_acct.setdefault(str(mr.get("account_id") or ""), []).append(mr)
        ranked_rows: List[Dict[str, Any]] = []
        for acct_id, rs in by_acct.items():
            ranked_rows.extend(rank_contacts_within_account(rs))

        mapped_df = pd.DataFrame(ranked_rows)
        write_csv(out_dir / f"contacts_mapped_{st}.csv", mapped_df, OUTPUT_COLUMNS)
        all_rows.extend(ranked_rows)

    all_df = pd.DataFrame(all_rows)
    write_csv(out_dir / "contacts_mapped_all.csv", all_df, OUTPUT_COLUMNS)

    # Review queue
    if not all_df.empty:
        rev_df = all_df[all_df["review_flag"].astype(str).str.lower() == "true"].copy()
    else:
        rev_df = pd.DataFrame(columns=OUTPUT_COLUMNS)
    write_csv(out_dir / "persona_review_queue.csv", rev_df, OUTPUT_COLUMNS)

    # Account committee summary
    summary_df = build_account_committee_summary(all_df if not all_df.empty else pd.DataFrame(columns=OUTPUT_COLUMNS))
    write_csv(out_dir / "account_buying_committee_summary.csv", summary_df, SUMMARY_COLUMNS)

    # Errors
    err_df = pd.DataFrame(all_errors)
    (out_dir / "persona_mapping_errors.csv").write_text(
        err_df.to_csv(index=False) if not err_df.empty else "state,contact_id,account_id,error,at\n",
        encoding="utf-8",
    )

    LOGGER.info("Done. Mapped=%s Review=%s Errors=%s", len(all_df), len(rev_df), len(err_df))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

