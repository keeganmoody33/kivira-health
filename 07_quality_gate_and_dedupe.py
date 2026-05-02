#!/usr/bin/env python3
"""
07_quality_gate_and_dedupe.py

Final QA + deduplication quality gate for Wave 1 outbound files.

Inputs (under ./output/):
- wave1_accounts_GA.csv
- wave1_accounts_NC.csv
- wave1_contacts_GA.csv
- wave1_contacts_NC.csv

Outputs (under ./output/):
- qa_pass_accounts_GA.csv
- qa_pass_accounts_NC.csv
- qa_pass_contacts_GA.csv
- qa_pass_contacts_NC.csv
- qa_review_accounts.csv
- qa_review_contacts.csv
- qa_rejected_accounts.csv
- qa_rejected_contacts.csv
- qa_summary.csv
- dedupe_conflicts.csv

No scraping. No inferred emails. No paid enrichment.
"""

from __future__ import annotations

import argparse
import dataclasses
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd
from dateutil.parser import isoparse

from tam_builder.pilot_filters import resolve_output_dir

try:
    from rapidfuzz import fuzz as _rapidfuzz_fuzz  # type: ignore
except Exception:  # noqa: BLE001
    _rapidfuzz_fuzz = None


LOGGER = logging.getLogger("kivira.qa")


REVIEW_CONTACT_COLUMNS: List[str] = [
    "contact_id",
    "account_id",
    "org_name",
    "parent_org_id",
    "primary_state",
    "subtier_primary",
    "person_name",
    "job_title",
    "persona_role_primary",
    "email",
    "phone_direct",
    "linkedin_profile_url",
    "buying_committee_fit_score",
    "wave_1_eligible_flag",
    "qa_status",
    "qa_reason",
    "dedupe_group_id",
    "dedupe_decision",
    "launch_blocker_flag",
    "evidence_notes",
    "last_verified_at",
]


REVIEW_ACCOUNT_COLUMNS: List[str] = [
    "account_id",
    "org_name",
    "parent_org_id",
    "primary_state",
    "subtier_primary",
    "primary_contact_id",
    "backup_contact_id",
    "economic_buyer_id",
    "committee_coverage_score",
    "account_readiness_score",
    "qa_status",
    "qa_reason",
    "dedupe_group_id",
    "dedupe_decision",
    "launch_blocker_flag",
    "evidence_notes",
    "last_verified_at",
]


QA_SUMMARY_COLUMNS: List[str] = [
    "state",
    "total_accounts",
    "passed_accounts",
    "review_accounts",
    "rejected_accounts",
    "total_contacts",
    "passed_contacts",
    "review_contacts",
    "rejected_contacts",
    "duplicate_logo_conflicts",
    "missing_primary_contact_count",
    "avg_account_readiness_score_passed",
    "avg_buying_committee_fit_score_passed",
    "last_verified_at",
]


DEDUPE_CONFLICT_COLUMNS: List[str] = [
    "conflict_type",
    "state",
    "dedupe_group_id",
    "entity_kind",
    "entity_id",
    "org_name",
    "person_name",
    "email",
    "linkedin_profile_url",
    "reason",
    "at",
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


def safe_float(value: Any) -> float:
    try:
        s = str(value or "").strip()
        return float(s) if s else 0.0
    except Exception:
        return 0.0


def boolish(v: Any) -> bool:
    return str(v or "").strip().lower() in {"true", "1", "yes"}


def as_bool_str(v: bool) -> str:
    return "true" if v else "false"


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
# Configurable thresholds
# ---------------------------
@dataclass(frozen=True)
class Thresholds:
    min_account_readiness_score: float = 0.62
    min_buying_committee_fit_score: float = 0.60
    min_committee_coverage_score: float = 0.40
    require_primary_contact: bool = True

    # Contact QA
    min_primary_contact_fit_score: float = 0.62
    reject_generic_inbox_email_for_primary: bool = True


GENERIC_INBOX_PREFIXES = (
    "info@",
    "contact@",
    "hello@",
    "support@",
    "sales@",
    "marketing@",
    "careers@",
    "hr@",
    "jobs@",
    "press@",
    "media@",
)


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


def normalize_person_key(person_name: str, job_title: str) -> str:
    return normalize_org_name(person_name) + "||" + normalize_org_name(job_title)


def is_generic_inbox_email(email: str) -> bool:
    e = (email or "").strip().lower()
    if not e or "@" not in e:
        return False
    return any(e.startswith(p) for p in GENERIC_INBOX_PREFIXES)


def dedupe_accounts(accounts_df: pd.DataFrame, conflicts: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Add dedupe_group_id and a default dedupe_decision for accounts.
    Dedupe key: parent_org_id (strongest) + state; else normalized org name + state.
    """
    df = accounts_df.copy()
    df["primary_state"] = df["primary_state"].astype(str).str.upper()
    df["org_name_norm"] = df["org_name"].astype(str).apply(normalize_org_name)
    df["parent_org_id"] = df["parent_org_id"].astype(str)

    def group_id(r: pd.Series) -> str:
        st = str(r.get("primary_state") or "").upper()
        pid = str(r.get("parent_org_id") or "").strip()
        if pid:
            return f"parent:{pid}::{st}"
        return f"org:{str(r.get('org_name_norm') or '')}::{st}"

    df["dedupe_group_id"] = df.apply(group_id, axis=1)
    df["dedupe_decision"] = "keep"

    # Detect duplicate groups
    for gid, g in df.groupby("dedupe_group_id", dropna=False):
        if len(g) <= 1:
            continue
        st = str(g["primary_state"].iloc[0] or "")
        # Conflict record
        for _, rr in g.iterrows():
            conflicts.append(
                {
                    "conflict_type": "duplicate_logo_group",
                    "state": st,
                    "dedupe_group_id": gid,
                    "entity_kind": "account",
                    "entity_id": str(rr.get("account_id") or ""),
                    "org_name": str(rr.get("org_name") or ""),
                    "person_name": "",
                    "email": "",
                    "linkedin_profile_url": "",
                    "reason": "Multiple accounts share same parent_org_id (or normalized org) within state",
                    "at": utc_now_iso(),
                }
            )
        # Decision: keep best readiness; others merge_review by default (never silently drop)
        g2 = g.copy()
        g2["readiness_num"] = g2["account_readiness_score"].apply(safe_float)
        g2["has_primary"] = g2["primary_contact_id"].astype(str).str.strip() != ""
        g2 = g2.sort_values(["has_primary", "readiness_num"], ascending=[False, False])
        keep_id = str(g2["account_id"].iloc[0])
        for idx, rr in g2.iterrows():
            if str(rr.get("account_id") or "") == keep_id:
                continue
            df.loc[df["account_id"] == rr.get("account_id"), "dedupe_decision"] = "merge_review"
    return df.drop(columns=["org_name_norm"], errors="ignore")


def dedupe_contacts(contacts_df: pd.DataFrame, conflicts: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Add dedupe_group_id and dedupe_decision for contacts.
    Dedupe key: normalized full name + normalized title + org name + state.
    Also flag email/linkedin collisions across different names.
    """
    df = contacts_df.copy()
    df["primary_state"] = df["primary_state"].astype(str).str.upper()
    df["org_name_norm"] = df["org_name"].astype(str).apply(normalize_org_name)
    df["person_key"] = df.apply(lambda r: normalize_person_key(str(r.get("person_name") or ""), str(r.get("job_title") or "")), axis=1)
    df["dedupe_group_id"] = df.apply(lambda r: f"person:{r.get('person_key')}::{r.get('org_name_norm')}::{r.get('primary_state')}", axis=1)
    df["dedupe_decision"] = "keep"

    # Within-account duplicates (same person_key)
    for gid, g in df.groupby("dedupe_group_id", dropna=False):
        if len(g) <= 1:
            continue
        st = str(g["primary_state"].iloc[0] or "")
        for _, rr in g.iterrows():
            conflicts.append(
                {
                    "conflict_type": "duplicate_person_group",
                    "state": st,
                    "dedupe_group_id": gid,
                    "entity_kind": "contact",
                    "entity_id": str(rr.get("contact_id") or ""),
                    "org_name": str(rr.get("org_name") or ""),
                    "person_name": str(rr.get("person_name") or ""),
                    "email": str(rr.get("email") or ""),
                    "linkedin_profile_url": str(rr.get("linkedin_profile_url") or ""),
                    "reason": "Duplicate person+title+org in state",
                    "at": utc_now_iso(),
                }
            )
        # Keep highest fit score
        g2 = g.copy()
        g2["fit_num"] = g2["buying_committee_fit_score"].apply(safe_float)
        g2 = g2.sort_values("fit_num", ascending=False)
        keep_id = str(g2["contact_id"].iloc[0])
        for _, rr in g2.iloc[1:].iterrows():
            df.loc[df["contact_id"] == rr.get("contact_id"), "dedupe_decision"] = "reject_duplicate"

    # Cross-name collisions for email / linkedin
    def _collision(field: str, conflict_type: str) -> None:
        s = df[field].astype(str).str.strip()
        if field == "email":
            s = s.str.lower()
        tmp = df.copy()
        tmp[field] = s
        tmp = tmp[tmp[field] != ""].copy()
        for val, g in tmp.groupby(field, dropna=False):
            if len(g) <= 1:
                continue
            names = {normalize_org_name(str(x)) for x in g["person_name"].astype(str).tolist() if str(x).strip()}
            if len(names) <= 1:
                continue
            st_counts = g["primary_state"].astype(str).value_counts().to_dict()
            for _, rr in g.iterrows():
                conflicts.append(
                    {
                        "conflict_type": conflict_type,
                        "state": str(rr.get("primary_state") or ""),
                        "dedupe_group_id": str(rr.get("dedupe_group_id") or ""),
                        "entity_kind": "contact",
                        "entity_id": str(rr.get("contact_id") or ""),
                        "org_name": str(rr.get("org_name") or ""),
                        "person_name": str(rr.get("person_name") or ""),
                        "email": str(rr.get("email") or ""),
                        "linkedin_profile_url": str(rr.get("linkedin_profile_url") or ""),
                        "reason": f"Same {field} attached to multiple different names (states={st_counts})",
                        "at": utc_now_iso(),
                    }
                )
            # Mark for review (never auto-reject)
            df.loc[df[field].astype(str).str.strip().str.lower() == str(val).strip().lower(), "dedupe_decision"] = "merge_review"

    _collision("email", "email_attached_to_multiple_names")
    _collision("linkedin_profile_url", "linkedin_attached_to_multiple_names")

    return df.drop(columns=["org_name_norm", "person_key"], errors="ignore")


def evaluate_account_qa(
    acct: Dict[str, Any],
    thresholds: Thresholds,
) -> Tuple[str, str, bool]:
    """
    Returns (qa_status, qa_reason, launch_blocker_flag)
    """
    readiness = safe_float(acct.get("account_readiness_score"))
    coverage = safe_float(acct.get("committee_coverage_score"))
    primary_contact_id = str(acct.get("primary_contact_id") or "").strip()
    subtier = str(acct.get("subtier_primary") or "").strip()

    reasons: List[str] = []
    status = "pass"
    blocker = False

    if thresholds.require_primary_contact and not primary_contact_id:
        status = "reject"
        blocker = True
        reasons.append("Reject: missing primary contact")

    if readiness < thresholds.min_account_readiness_score:
        if status != "reject":
            status = "review" if readiness >= (thresholds.min_account_readiness_score - 0.12) else "reject"
        if readiness < (thresholds.min_account_readiness_score - 0.12):
            blocker = True
        reasons.append("Low account_readiness_score")

    if coverage < thresholds.min_committee_coverage_score:
        if status == "pass":
            status = "review"
        reasons.append("Weak committee coverage")

    if not subtier:
        if status == "pass":
            status = "review"
        reasons.append("Subtier ambiguity (missing subtier_primary)")

    if status == "pass":
        reasons.insert(0, "Pass: sufficient readiness and primary contact")

    reason = "; ".join(reasons) if reasons else "Pass"
    return status, reason, blocker


def evaluate_contact_qa(
    contact: Dict[str, Any],
    thresholds: Thresholds,
    *,
    is_primary_for_account: bool,
    demo_bookable_flag: bool,
) -> Tuple[str, str, bool]:
    """
    Returns (qa_status, qa_reason, launch_blocker_flag)
    """
    name = str(contact.get("person_name") or "").strip()
    title = str(contact.get("job_title") or "").strip()
    email = str(contact.get("email") or "").strip()
    linkedin = str(contact.get("linkedin_profile_url") or "").strip()
    fit = safe_float(contact.get("buying_committee_fit_score"))
    role = str(contact.get("persona_role_primary") or "").strip()

    reasons: List[str] = []
    status = "pass"
    blocker = False

    if not name or not title:
        status = "review"
        reasons.append("Missing name or title")
        if is_primary_for_account:
            blocker = True

    if fit < thresholds.min_buying_committee_fit_score:
        if is_primary_for_account and fit < thresholds.min_primary_contact_fit_score:
            status = "reject"
            blocker = True
            reasons.append("Reject: primary contact fit score too low")
        else:
            if status != "reject":
                status = "review"
            reasons.append("Weak role fit score")

    if is_primary_for_account and not demo_bookable_flag:
        status = "reject"
        blocker = True
        reasons.append("Reject: selected primary is not demo-bookable")

    if is_primary_for_account and thresholds.reject_generic_inbox_email_for_primary and is_generic_inbox_email(email):
        status = "reject"
        blocker = True
        reasons.append("Reject: generic inbox email selected as primary")

    # Weak evidence: no direct contact path at all
    has_contact_path = bool(email) or bool(str(contact.get("phone_direct") or "").strip()) or bool(linkedin)
    if is_primary_for_account and not has_contact_path:
        status = "reject"
        blocker = True
        reasons.append("Reject: missing contact path entirely")

    if status == "pass":
        reasons.insert(0, "Pass: adequate identity/title evidence for outreach")

    return status, "; ".join(reasons) if reasons else "Pass", blocker


def build_qa_summary(
    accounts_reviewed: pd.DataFrame,
    contacts_reviewed: pd.DataFrame,
    conflicts: pd.DataFrame,
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    now = utc_now_iso()

    for state in sorted(set(accounts_reviewed["primary_state"].astype(str).str.upper().tolist())):
        a = accounts_reviewed[accounts_reviewed["primary_state"].astype(str).str.upper() == state].copy()
        c = contacts_reviewed[contacts_reviewed["primary_state"].astype(str).str.upper() == state].copy()

        total_a = len(a)
        passed_a = int((a["qa_status"] == "pass").sum())
        review_a = int((a["qa_status"] == "review").sum())
        reject_a = int((a["qa_status"] == "reject").sum())

        total_c = len(c)
        passed_c = int((c["qa_status"] == "pass").sum())
        review_c = int((c["qa_status"] == "review").sum())
        reject_c = int((c["qa_status"] == "reject").sum())

        dup_conflicts = int((conflicts["conflict_type"] == "duplicate_logo_group").sum()) if not conflicts.empty else 0
        missing_primary = int((a["primary_contact_id"].astype(str).str.strip() == "").sum())

        avg_ready_passed = a[a["qa_status"] == "pass"]["account_readiness_score"].apply(safe_float).mean() if passed_a else 0.0
        avg_fit_passed = c[c["qa_status"] == "pass"]["buying_committee_fit_score"].apply(safe_float).mean() if passed_c else 0.0

        rows.append(
            {
                "state": state,
                "total_accounts": int(total_a),
                "passed_accounts": passed_a,
                "review_accounts": review_a,
                "rejected_accounts": reject_a,
                "total_contacts": int(total_c),
                "passed_contacts": passed_c,
                "review_contacts": review_c,
                "rejected_contacts": reject_c,
                "duplicate_logo_conflicts": dup_conflicts,
                "missing_primary_contact_count": missing_primary,
                "avg_account_readiness_score_passed": f"{avg_ready_passed:.2f}",
                "avg_buying_committee_fit_score_passed": f"{avg_fit_passed:.2f}",
                "last_verified_at": now,
            }
        )

    df = pd.DataFrame(rows)
    for c in QA_SUMMARY_COLUMNS:
        if c not in df.columns:
            df[c] = ""
    return df[QA_SUMMARY_COLUMNS]


def _ensure_cols(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Final QA + dedupe gate for Wave 1 outbound lists.")
    p.add_argument("--base-dir", default=".", help="Base directory containing output/.")
    p.add_argument("--states", default="GA,NC", help="Comma-separated states to process.")
    p.add_argument("--log-level", default="INFO", help="Logging level.")
    p.add_argument(
        "--output-subdir",
        default="",
        help="Read/write under output/<subdir>/ (e.g. pilot).",
    )
    args = p.parse_args(argv)

    logging.basicConfig(level=getattr(logging, str(args.log_level).upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s - %(message)s")

    base_dir = Path(args.base_dir).expanduser().resolve()
    out_dir = resolve_output_dir(base_dir, str(args.output_subdir or ""))

    thresholds = Thresholds()

    states = [s.strip().upper() for s in str(args.states).split(",") if s.strip()]

    accounts_all: List[pd.DataFrame] = []
    contacts_all: List[pd.DataFrame] = []

    for st in states:
        a_path = out_dir / f"wave1_accounts_{st}.csv"
        c_path = out_dir / f"wave1_contacts_{st}.csv"
        if not a_path.exists() or not c_path.exists():
            LOGGER.warning("Missing inputs for %s (skipping): %s %s", st, a_path, c_path)
            continue
        accounts_all.append(pd.read_csv(a_path, dtype=str).fillna(""))
        contacts_all.append(pd.read_csv(c_path, dtype=str).fillna(""))

    accounts_df = pd.concat(accounts_all, ignore_index=True) if accounts_all else pd.DataFrame()
    contacts_df = pd.concat(contacts_all, ignore_index=True) if contacts_all else pd.DataFrame()

    accounts_df = _ensure_cols(accounts_df, REVIEW_ACCOUNT_COLUMNS + ["account_readiness_score", "committee_coverage_score", "wave_status", "review_reason"])
    contacts_df = _ensure_cols(contacts_df, REVIEW_CONTACT_COLUMNS + ["demo_bookable_flag", "preferred_contact_flag", "backup_contact_flag"])

    accounts_df["primary_state"] = accounts_df["primary_state"].astype(str).str.upper()
    contacts_df["primary_state"] = contacts_df["primary_state"].astype(str).str.upper()

    # Build lookup: account -> primary contact id and demo-bookable flags
    acct_primary: Dict[str, str] = {str(r.get("account_id") or ""): str(r.get("primary_contact_id") or "") for r in accounts_df.to_dict(orient="records")}
    demo_map: Dict[str, bool] = {str(r.get("contact_id") or ""): boolish(r.get("demo_bookable_flag")) for r in contacts_df.to_dict(orient="records")}

    conflicts: List[Dict[str, Any]] = []
    accounts_df = dedupe_accounts(accounts_df, conflicts)
    contacts_df = dedupe_contacts(contacts_df, conflicts)

    # Evaluate QA for accounts
    reviewed_accounts: List[Dict[str, Any]] = []
    for r in accounts_df.to_dict(orient="records"):
        qa_status, qa_reason, blocker = evaluate_account_qa(r, thresholds)
        out = {c: "" for c in REVIEW_ACCOUNT_COLUMNS}
        out.update(
            {
                "account_id": str(r.get("account_id") or ""),
                "org_name": str(r.get("org_name") or ""),
                "parent_org_id": str(r.get("parent_org_id") or ""),
                "primary_state": str(r.get("primary_state") or ""),
                "subtier_primary": str(r.get("subtier_primary") or ""),
                "primary_contact_id": str(r.get("primary_contact_id") or ""),
                "backup_contact_id": str(r.get("backup_contact_id") or ""),
                "economic_buyer_id": str(r.get("economic_buyer_id") or ""),
                "committee_coverage_score": str(r.get("committee_coverage_score") or ""),
                "account_readiness_score": str(r.get("account_readiness_score") or ""),
                "qa_status": qa_status,
                "qa_reason": qa_reason,
                "dedupe_group_id": str(r.get("dedupe_group_id") or ""),
                "dedupe_decision": str(r.get("dedupe_decision") or "keep"),
                "launch_blocker_flag": as_bool_str(blocker),
                "evidence_notes": str(r.get("evidence_notes") or ""),
                "last_verified_at": parse_iso_or_now(r.get("last_verified_at")),
            }
        )
        reviewed_accounts.append(out)

    accounts_reviewed_df = pd.DataFrame(reviewed_accounts)
    for c in REVIEW_ACCOUNT_COLUMNS:
        if c not in accounts_reviewed_df.columns:
            accounts_reviewed_df[c] = ""

    # Evaluate QA for contacts
    reviewed_contacts: List[Dict[str, Any]] = []
    for r in contacts_df.to_dict(orient="records"):
        account_id = str(r.get("account_id") or "")
        contact_id = str(r.get("contact_id") or "")
        is_primary = acct_primary.get(account_id, "") == contact_id
        demo_bookable = demo_map.get(contact_id, boolish(r.get("demo_bookable_flag")))
        qa_status, qa_reason, blocker = evaluate_contact_qa(r, thresholds, is_primary_for_account=is_primary, demo_bookable_flag=demo_bookable)

        out = {c: "" for c in REVIEW_CONTACT_COLUMNS}
        out.update(
            {
                "contact_id": contact_id,
                "account_id": account_id,
                "org_name": str(r.get("org_name") or ""),
                "parent_org_id": str(r.get("parent_org_id") or ""),
                "primary_state": str(r.get("primary_state") or ""),
                "subtier_primary": str(r.get("subtier_primary") or ""),
                "person_name": str(r.get("person_name") or ""),
                "job_title": str(r.get("job_title") or ""),
                "persona_role_primary": str(r.get("persona_role_primary") or ""),
                "email": str(r.get("email") or ""),
                "phone_direct": str(r.get("phone_direct") or ""),
                "linkedin_profile_url": str(r.get("linkedin_profile_url") or ""),
                "buying_committee_fit_score": str(r.get("buying_committee_fit_score") or ""),
                "wave_1_eligible_flag": str(r.get("wave_1_eligible_flag") or ""),
                "qa_status": qa_status,
                "qa_reason": qa_reason,
                "dedupe_group_id": str(r.get("dedupe_group_id") or ""),
                "dedupe_decision": str(r.get("dedupe_decision") or "keep"),
                "launch_blocker_flag": as_bool_str(blocker),
                "evidence_notes": str(r.get("evidence_notes") or ""),
                "last_verified_at": parse_iso_or_now(r.get("last_verified_at")),
            }
        )
        reviewed_contacts.append(out)

    contacts_reviewed_df = pd.DataFrame(reviewed_contacts)
    for c in REVIEW_CONTACT_COLUMNS:
        if c not in contacts_reviewed_df.columns:
            contacts_reviewed_df[c] = ""

    # Split into pass/review/reject
    pass_accounts = accounts_reviewed_df[accounts_reviewed_df["qa_status"] == "pass"].copy()
    review_accounts = accounts_reviewed_df[accounts_reviewed_df["qa_status"] == "review"].copy()
    reject_accounts = accounts_reviewed_df[accounts_reviewed_df["qa_status"] == "reject"].copy()

    pass_contacts = contacts_reviewed_df[contacts_reviewed_df["qa_status"] == "pass"].copy()
    review_contacts = contacts_reviewed_df[contacts_reviewed_df["qa_status"] == "review"].copy()
    reject_contacts = contacts_reviewed_df[contacts_reviewed_df["qa_status"] == "reject"].copy()

    # State-specific pass outputs
    for st in states:
        st = st.strip().upper()
        pass_accounts[pass_accounts["primary_state"].astype(str).str.upper() == st].to_csv(out_dir / f"qa_pass_accounts_{st}.csv", index=False)
        pass_contacts[pass_contacts["primary_state"].astype(str).str.upper() == st].to_csv(out_dir / f"qa_pass_contacts_{st}.csv", index=False)

    review_accounts.to_csv(out_dir / "qa_review_accounts.csv", index=False)
    review_contacts.to_csv(out_dir / "qa_review_contacts.csv", index=False)
    reject_accounts.to_csv(out_dir / "qa_rejected_accounts.csv", index=False)
    reject_contacts.to_csv(out_dir / "qa_rejected_contacts.csv", index=False)

    conflicts_df = pd.DataFrame(conflicts)
    for c in DEDUPE_CONFLICT_COLUMNS:
        if c not in conflicts_df.columns:
            conflicts_df[c] = ""
    conflicts_df[DEDUPE_CONFLICT_COLUMNS].to_csv(out_dir / "dedupe_conflicts.csv", index=False)

    summary_df = build_qa_summary(accounts_reviewed_df, contacts_reviewed_df, conflicts_df)
    summary_df.to_csv(out_dir / "qa_summary.csv", index=False)

    LOGGER.info(
        "QA complete. Accounts pass=%s review=%s reject=%s; Contacts pass=%s review=%s reject=%s; Conflicts=%s",
        len(pass_accounts),
        len(review_accounts),
        len(reject_accounts),
        len(pass_contacts),
        len(review_contacts),
        len(reject_contacts),
        len(conflicts_df),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

