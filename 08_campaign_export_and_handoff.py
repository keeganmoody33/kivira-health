#!/usr/bin/env python3
"""
08_campaign_export_and_handoff.py

Package QA-approved Wave 1 outbound records into campaign-ready exports and operator handoff files.

Inputs (under ./output/):
- qa_pass_accounts_GA.csv
- qa_pass_accounts_NC.csv
- qa_pass_contacts_GA.csv
- qa_pass_contacts_NC.csv
- qa_review_accounts.csv
- qa_review_contacts.csv
- qa_rejected_accounts.csv
- qa_rejected_contacts.csv

Outputs (under ./output/):
- campaign_contacts_GA.csv
- campaign_contacts_NC.csv
- campaign_contacts_all.csv
- campaign_accounts_GA.csv
- campaign_accounts_NC.csv
- campaign_accounts_all.csv
- campaign_suppressions.csv
- operator_handoff_report.csv
- launch_summary.csv

Campaign status values:
- ready_to_launch: included in campaign exports
- hold_for_review: included in operator handoff, excluded from campaign exports
- suppressed: included in suppressions, excluded from campaign exports

Execution (after you have run 01→07 and produced QA outputs):
    python3 08_campaign_export_and_handoff.py --base-dir . --states GA,NC
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd
from dateutil.parser import isoparse

from tam_builder.pilot_filters import resolve_output_dir


LOGGER = logging.getLogger("kivira.handoff")


CONTACT_EXPORT_COLUMNS: List[str] = [
    "contact_id",
    "account_id",
    "org_name",
    "parent_org_id",
    "primary_state",
    "subtier_primary",
    "person_name",
    "first_name",
    "last_name",
    "job_title",
    "persona_role_primary",
    "persona_role_secondary",
    "outreach_sequence_stage",
    "email",
    "phone_direct",
    "phone_main",
    "linkedin_profile_url",
    "source_url",
    "campaign_status",
    "campaign_reason",
    "owner_state_queue",
    "priority_band",
    "evidence_notes",
    "last_verified_at",
]


ACCOUNT_EXPORT_COLUMNS: List[str] = [
    "account_id",
    "org_name",
    "parent_org_id",
    "primary_state",
    "subtier_primary",
    "primary_contact_id",
    "primary_contact_name",
    "primary_contact_title",
    "backup_contact_id",
    "backup_contact_name",
    "backup_contact_title",
    "economic_buyer_id",
    "economic_buyer_name",
    "technical_gatekeeper_id",
    "committee_coverage_score",
    "account_readiness_score",
    "priority_band",
    "campaign_status",
    "campaign_reason",
    "evidence_notes",
    "last_verified_at",
]


SUPPRESSION_COLUMNS: List[str] = [
    "record_type",
    "record_id",
    "org_name",
    "person_name",
    "email",
    "reason",
    "source_file",
    "last_verified_at",
]


OPERATOR_HANDOFF_COLUMNS: List[str] = [
    "account_id",
    "org_name",
    "primary_state",
    "subtier_primary",
    "recommended_primary_contact",
    "recommended_backup_contact",
    "recommended_economic_buyer",
    "recommended_sequence",
    "committee_gap_notes",
    "launch_notes",
    "risk_notes",
    "manual_review_needed_flag",
    "manual_review_reason",
    "last_verified_at",
]


LAUNCH_SUMMARY_COLUMNS: List[str] = [
    "state",
    "total_ready_accounts",
    "total_ready_contacts",
    "total_suppressed_records",
    "tier_1_ready_accounts",
    "tier_2_ready_accounts",
    "tier_3_ready_accounts",
    "avg_account_readiness_score",
    "last_verified_at",
]


ROLE_OPERATIONAL_OWNER = "Operational Owner"
ROLE_CLINICAL_CHAMPION = "Clinical Champion"
ROLE_ECONOMIC_BUYER = "Economic Buyer"
ROLE_TECH_GATEKEEPER = "Technical Gatekeeper"
ROLE_BH_QUALITY = "BH / Quality Influencer"


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


def boolish(value: Any) -> bool:
    return str(value or "").strip().lower() in {"true", "1", "yes"}


def _ensure_cols(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df


@dataclass(frozen=True)
class PriorityBands:
    p1_min_readiness: float = 0.78
    p2_min_readiness: float = 0.62


def assign_priority_band(subtier_primary: str, readiness_score: float, bands: PriorityBands) -> str:
    """
    Priority band heuristic combining readiness and subtier attractiveness.
    """
    st = (subtier_primary or "").strip().upper()
    # Readiness thresholds
    if readiness_score >= bands.p1_min_readiness:
        return "P1"
    if readiness_score >= bands.p2_min_readiness:
        # Promote attractive subtiers
        if st in {"1C", "1A"}:
            return "P1"
        return "P2"
    return "P3"


def build_campaign_contact_export(
    pass_contacts: pd.DataFrame,
    pass_accounts: pd.DataFrame,
    bands: PriorityBands,
) -> pd.DataFrame:
    """
    Build campaign contacts export from pass QA contacts only.
    """
    c = pass_contacts.copy()
    a = pass_accounts.copy()

    c = _ensure_cols(
        c,
        [
            "contact_id",
            "account_id",
            "org_name",
            "parent_org_id",
            "primary_state",
            "subtier_primary",
            "person_name",
            "first_name",
            "last_name",
            "job_title",
            "persona_role_primary",
            "persona_role_secondary",
            "outreach_sequence_stage",
            "email",
            "phone_direct",
            "phone_main",
            "linkedin_profile_url",
            "source_url",
            "evidence_notes",
            "last_verified_at",
        ],
    )
    a = _ensure_cols(a, ["account_id", "primary_state", "subtier_primary", "account_readiness_score"])

    # Join readiness to contacts for priority assignment
    readiness_map = {str(r["account_id"]): safe_float(r.get("account_readiness_score")) for r in a.to_dict(orient="records")}
    subtier_map = {str(r["account_id"]): str(r.get("subtier_primary") or "") for r in a.to_dict(orient="records")}
    state_map = {str(r["account_id"]): str(r.get("primary_state") or "") for r in a.to_dict(orient="records")}

    rows: List[Dict[str, Any]] = []
    for r in c.to_dict(orient="records"):
        account_id = str(r.get("account_id") or "")
        st = str(state_map.get(account_id) or r.get("primary_state") or "").upper()
        subtier = str(subtier_map.get(account_id) or r.get("subtier_primary") or "")
        readiness = readiness_map.get(account_id, 0.0)
        priority = assign_priority_band(subtier, readiness, bands)

        campaign_status = "ready_to_launch"
        campaign_reason = "QA pass"
        owner_state_queue = st

        out = {c2: "" for c2 in CONTACT_EXPORT_COLUMNS}
        out.update(
            {
                "contact_id": str(r.get("contact_id") or ""),
                "account_id": account_id,
                "org_name": str(r.get("org_name") or ""),
                "parent_org_id": str(r.get("parent_org_id") or ""),
                "primary_state": st,
                "subtier_primary": str(subtier).upper(),
                "person_name": str(r.get("person_name") or ""),
                "first_name": str(r.get("first_name") or ""),
                "last_name": str(r.get("last_name") or ""),
                "job_title": str(r.get("job_title") or ""),
                "persona_role_primary": str(r.get("persona_role_primary") or ""),
                "persona_role_secondary": str(r.get("persona_role_secondary") or ""),
                "outreach_sequence_stage": str(r.get("outreach_sequence_stage") or ""),
                "email": str(r.get("email") or ""),
                "phone_direct": str(r.get("phone_direct") or ""),
                "phone_main": str(r.get("phone_main") or ""),
                "linkedin_profile_url": str(r.get("linkedin_profile_url") or ""),
                "source_url": str(r.get("source_url") or ""),
                "campaign_status": campaign_status,
                "campaign_reason": campaign_reason,
                "owner_state_queue": owner_state_queue,
                "priority_band": priority,
                "evidence_notes": str(r.get("evidence_notes") or ""),
                "last_verified_at": parse_iso_or_now(r.get("last_verified_at")),
            }
        )
        rows.append(out)

    df = pd.DataFrame(rows)
    df = _ensure_cols(df, CONTACT_EXPORT_COLUMNS)
    return df[CONTACT_EXPORT_COLUMNS]


def _contact_label(r: Dict[str, Any]) -> str:
    name = str(r.get("person_name") or "").strip()
    title = str(r.get("job_title") or "").strip()
    role = str(r.get("persona_role_primary") or "").strip()
    parts = [p for p in [name, title, role] if p]
    return " — ".join(parts)


def build_campaign_account_export(
    pass_accounts: pd.DataFrame,
    pass_contacts: pd.DataFrame,
    bands: PriorityBands,
) -> pd.DataFrame:
    a = pass_accounts.copy()
    c = pass_contacts.copy()

    a = _ensure_cols(
        a,
        [
            "account_id",
            "org_name",
            "parent_org_id",
            "primary_state",
            "subtier_primary",
            "primary_contact_id",
            "backup_contact_id",
            "economic_buyer_id",
            "technical_gatekeeper_id",
            "committee_coverage_score",
            "account_readiness_score",
            "evidence_notes",
            "last_verified_at",
        ],
    )
    c = _ensure_cols(
        c,
        [
            "contact_id",
            "account_id",
            "person_name",
            "job_title",
            "persona_role_primary",
            "evidence_notes",
        ],
    )

    # Build contact lookup by contact_id
    contact_by_id = {str(r.get("contact_id") or ""): r for r in c.to_dict(orient="records") if str(r.get("contact_id") or "").strip()}

    rows: List[Dict[str, Any]] = []
    for r in a.to_dict(orient="records"):
        account_id = str(r.get("account_id") or "")
        st = str(r.get("primary_state") or "").upper()
        subtier = str(r.get("subtier_primary") or "").upper()
        readiness = safe_float(r.get("account_readiness_score"))
        priority = assign_priority_band(subtier, readiness, bands)

        primary_id = str(r.get("primary_contact_id") or "")
        backup_id = str(r.get("backup_contact_id") or "")
        eb_id = str(r.get("economic_buyer_id") or "")
        tg_id = str(r.get("technical_gatekeeper_id") or "")

        primary = contact_by_id.get(primary_id, {})
        backup = contact_by_id.get(backup_id, {})
        eb = contact_by_id.get(eb_id, {})

        out = {c2: "" for c2 in ACCOUNT_EXPORT_COLUMNS}
        out.update(
            {
                "account_id": account_id,
                "org_name": str(r.get("org_name") or ""),
                "parent_org_id": str(r.get("parent_org_id") or ""),
                "primary_state": st,
                "subtier_primary": subtier,
                "primary_contact_id": primary_id,
                "primary_contact_name": str(primary.get("person_name") or ""),
                "primary_contact_title": str(primary.get("job_title") or ""),
                "backup_contact_id": backup_id,
                "backup_contact_name": str(backup.get("person_name") or ""),
                "backup_contact_title": str(backup.get("job_title") or ""),
                "economic_buyer_id": eb_id,
                "economic_buyer_name": str(eb.get("person_name") or ""),
                "technical_gatekeeper_id": tg_id,
                "committee_coverage_score": str(r.get("committee_coverage_score") or ""),
                "account_readiness_score": f"{readiness:.2f}",
                "priority_band": priority,
                "campaign_status": "ready_to_launch",
                "campaign_reason": "QA pass",
                "evidence_notes": str(r.get("evidence_notes") or ""),
                "last_verified_at": parse_iso_or_now(r.get("last_verified_at")),
            }
        )
        rows.append(out)

    df = pd.DataFrame(rows)
    df = _ensure_cols(df, ACCOUNT_EXPORT_COLUMNS)
    return df[ACCOUNT_EXPORT_COLUMNS]


def build_suppressions(
    review_accounts: pd.DataFrame,
    review_contacts: pd.DataFrame,
    rejected_accounts: pd.DataFrame,
    rejected_contacts: pd.DataFrame,
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    now = utc_now_iso()

    def add(record_type: str, record_id: str, org_name: str, person_name: str, email: str, reason: str, source_file: str, last_verified_at: Any) -> None:
        rows.append(
            {
                "record_type": record_type,
                "record_id": record_id,
                "org_name": org_name,
                "person_name": person_name,
                "email": email,
                "reason": reason,
                "source_file": source_file,
                "last_verified_at": parse_iso_or_now(last_verified_at) if last_verified_at else now,
            }
        )

    for df, src, status in [
        (review_accounts, "qa_review_accounts.csv", "hold_for_review"),
        (rejected_accounts, "qa_rejected_accounts.csv", "suppressed"),
    ]:
        if df is None or df.empty:
            continue
        df = _ensure_cols(df, ["account_id", "org_name", "qa_reason", "last_verified_at"])
        for r in df.to_dict(orient="records"):
            add("account", str(r.get("account_id") or ""), str(r.get("org_name") or ""), "", "", f"{status}: {r.get('qa_reason')}", src, r.get("last_verified_at"))

    for df, src, status in [
        (review_contacts, "qa_review_contacts.csv", "hold_for_review"),
        (rejected_contacts, "qa_rejected_contacts.csv", "suppressed"),
    ]:
        if df is None or df.empty:
            continue
        df = _ensure_cols(df, ["contact_id", "org_name", "person_name", "email", "qa_reason", "last_verified_at"])
        for r in df.to_dict(orient="records"):
            add(
                "contact",
                str(r.get("contact_id") or ""),
                str(r.get("org_name") or ""),
                str(r.get("person_name") or ""),
                str(r.get("email") or ""),
                f"{status}: {r.get('qa_reason')}",
                src,
                r.get("last_verified_at"),
            )

    df_out = pd.DataFrame(rows)
    df_out = _ensure_cols(df_out, SUPPRESSION_COLUMNS)
    return df_out[SUPPRESSION_COLUMNS]


def build_operator_handoff_report(
    pass_accounts: pd.DataFrame,
    pass_contacts: pd.DataFrame,
    review_accounts: pd.DataFrame,
    review_contacts: pd.DataFrame,
) -> pd.DataFrame:
    """
    Produce an operator-facing report across pass + review accounts.
    """
    now = utc_now_iso()
    pass_accounts = pass_accounts.copy() if pass_accounts is not None else pd.DataFrame()
    review_accounts = review_accounts.copy() if review_accounts is not None else pd.DataFrame()
    pass_contacts = pass_contacts.copy() if pass_contacts is not None else pd.DataFrame()
    review_contacts = review_contacts.copy() if review_contacts is not None else pd.DataFrame()

    # Use both pass + review for handoff
    accounts = pd.concat([pass_accounts, review_accounts], ignore_index=True) if not pass_accounts.empty or not review_accounts.empty else pd.DataFrame()
    contacts = pd.concat([pass_contacts, review_contacts], ignore_index=True) if not pass_contacts.empty or not review_contacts.empty else pd.DataFrame()

    accounts = _ensure_cols(
        accounts,
        ["account_id", "org_name", "primary_state", "subtier_primary", "primary_contact_id", "backup_contact_id", "economic_buyer_id", "qa_status", "qa_reason", "last_verified_at"],
    )
    contacts = _ensure_cols(
        contacts,
        ["contact_id", "account_id", "person_name", "job_title", "persona_role_primary", "outreach_sequence_stage", "buying_committee_fit_score", "evidence_notes"],
    )
    contact_by_id = {str(r.get("contact_id") or ""): r for r in contacts.to_dict(orient="records") if str(r.get("contact_id") or "").strip()}

    rows: List[Dict[str, Any]] = []
    for r in accounts.to_dict(orient="records"):
        account_id = str(r.get("account_id") or "")
        st = str(r.get("primary_state") or "").upper()
        subtier = str(r.get("subtier_primary") or "").upper()
        primary = contact_by_id.get(str(r.get("primary_contact_id") or ""), {})
        backup = contact_by_id.get(str(r.get("backup_contact_id") or ""), {})
        eb = contact_by_id.get(str(r.get("economic_buyer_id") or ""), {})

        # Sequence suggestion
        seq = "Operator first, Clinical Champion second, Economic Buyer third"
        if str(primary.get("persona_role_primary") or "") == ROLE_ECONOMIC_BUYER and subtier == "1B":
            seq = "Physician Owner first, Practice Administrator parallel"
        if str(primary.get("persona_role_primary") or "") == ROLE_OPERATIONAL_OWNER:
            seq = "Operator first, Technical Gatekeeper parallel, Economic Buyer later"

        manual_review = str(r.get("qa_status") or "").strip().lower() != "pass"
        manual_reason = str(r.get("qa_reason") or "").strip()

        rows.append(
            {
                "account_id": account_id,
                "org_name": str(r.get("org_name") or ""),
                "primary_state": st,
                "subtier_primary": subtier,
                "recommended_primary_contact": _contact_label(primary),
                "recommended_backup_contact": _contact_label(backup),
                "recommended_economic_buyer": _contact_label(eb),
                "recommended_sequence": seq,
                "committee_gap_notes": "",
                "launch_notes": "QA pass" if not manual_review else "Hold for review",
                "risk_notes": manual_reason,
                "manual_review_needed_flag": "true" if manual_review else "false",
                "manual_review_reason": manual_reason,
                "last_verified_at": parse_iso_or_now(r.get("last_verified_at")) or now,
            }
        )

    df = pd.DataFrame(rows)
    df = _ensure_cols(df, OPERATOR_HANDOFF_COLUMNS)
    return df[OPERATOR_HANDOFF_COLUMNS]


def build_launch_summary(
    campaign_accounts_all: pd.DataFrame,
    campaign_contacts_all: pd.DataFrame,
    suppressions: pd.DataFrame,
) -> pd.DataFrame:
    now = utc_now_iso()
    a = campaign_accounts_all.copy() if campaign_accounts_all is not None else pd.DataFrame()
    c = campaign_contacts_all.copy() if campaign_contacts_all is not None else pd.DataFrame()
    s = suppressions.copy() if suppressions is not None else pd.DataFrame()

    a = _ensure_cols(a, ["primary_state", "subtier_primary", "account_readiness_score"])
    c = _ensure_cols(c, ["primary_state"])
    s = _ensure_cols(s, ["record_type"])

    rows: List[Dict[str, Any]] = []
    for state in sorted(set(a["primary_state"].astype(str).str.upper().tolist())):
        aa = a[a["primary_state"].astype(str).str.upper() == state].copy()
        cc = c[c["primary_state"].astype(str).str.upper() == state].copy()

        tier1 = int((aa["subtier_primary"].astype(str).str.startswith("1")).sum())
        tier2 = int((aa["subtier_primary"].astype(str).str.startswith("2")).sum())
        tier3 = int((aa["subtier_primary"].astype(str).str.startswith("3")).sum())

        rows.append(
            {
                "state": state,
                "total_ready_accounts": int(len(aa)),
                "total_ready_contacts": int(len(cc)),
                "total_suppressed_records": int(len(s)),
                "tier_1_ready_accounts": tier1,
                "tier_2_ready_accounts": tier2,
                "tier_3_ready_accounts": tier3,
                "avg_account_readiness_score": f"{aa['account_readiness_score'].apply(lambda x: float(x) if str(x).strip() else 0.0).mean():.2f}" if len(aa) else "0.00",
                "last_verified_at": now,
            }
        )
    df = pd.DataFrame(rows)
    df = _ensure_cols(df, LAUNCH_SUMMARY_COLUMNS)
    return df[LAUNCH_SUMMARY_COLUMNS]


def read_csv_safe(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path, dtype=str).fillna("")
    except Exception:
        return pd.DataFrame()


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Campaign export + operator handoff packaging.")
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

    states = [s.strip().upper() for s in str(args.states).split(",") if s.strip()]
    bands = PriorityBands()

    pass_accounts_by_state: Dict[str, pd.DataFrame] = {}
    pass_contacts_by_state: Dict[str, pd.DataFrame] = {}

    for st in states:
        pass_accounts_by_state[st] = read_csv_safe(out_dir / f"qa_pass_accounts_{st}.csv")
        pass_contacts_by_state[st] = read_csv_safe(out_dir / f"qa_pass_contacts_{st}.csv")

    review_accounts = read_csv_safe(out_dir / "qa_review_accounts.csv")
    review_contacts = read_csv_safe(out_dir / "qa_review_contacts.csv")
    rejected_accounts = read_csv_safe(out_dir / "qa_rejected_accounts.csv")
    rejected_contacts = read_csv_safe(out_dir / "qa_rejected_contacts.csv")

    # Build exports per state + all-state
    campaign_accounts_all: List[pd.DataFrame] = []
    campaign_contacts_all: List[pd.DataFrame] = []

    for st in states:
        pa = pass_accounts_by_state.get(st, pd.DataFrame())
        pc = pass_contacts_by_state.get(st, pd.DataFrame())
        if pa.empty and pc.empty:
            LOGGER.warning("No pass records for %s", st)
        contacts_export = build_campaign_contact_export(pc, pa, bands)
        accounts_export = build_campaign_account_export(pa, pc, bands)

        contacts_export.to_csv(out_dir / f"campaign_contacts_{st}.csv", index=False)
        accounts_export.to_csv(out_dir / f"campaign_accounts_{st}.csv", index=False)

        campaign_contacts_all.append(contacts_export)
        campaign_accounts_all.append(accounts_export)

    contacts_all = pd.concat(campaign_contacts_all, ignore_index=True) if campaign_contacts_all else pd.DataFrame(columns=CONTACT_EXPORT_COLUMNS)
    accounts_all = pd.concat(campaign_accounts_all, ignore_index=True) if campaign_accounts_all else pd.DataFrame(columns=ACCOUNT_EXPORT_COLUMNS)

    contacts_all = _ensure_cols(contacts_all, CONTACT_EXPORT_COLUMNS)[CONTACT_EXPORT_COLUMNS]
    accounts_all = _ensure_cols(accounts_all, ACCOUNT_EXPORT_COLUMNS)[ACCOUNT_EXPORT_COLUMNS]

    contacts_all.to_csv(out_dir / "campaign_contacts_all.csv", index=False)
    accounts_all.to_csv(out_dir / "campaign_accounts_all.csv", index=False)

    suppressions = build_suppressions(review_accounts, review_contacts, rejected_accounts, rejected_contacts)
    suppressions.to_csv(out_dir / "campaign_suppressions.csv", index=False)

    handoff = build_operator_handoff_report(
        pass_accounts=pd.concat(list(pass_accounts_by_state.values()), ignore_index=True) if pass_accounts_by_state else pd.DataFrame(),
        pass_contacts=pd.concat(list(pass_contacts_by_state.values()), ignore_index=True) if pass_contacts_by_state else pd.DataFrame(),
        review_accounts=review_accounts,
        review_contacts=review_contacts,
    )
    handoff.to_csv(out_dir / "operator_handoff_report.csv", index=False)

    launch_summary = build_launch_summary(accounts_all, contacts_all, suppressions)
    launch_summary.to_csv(out_dir / "launch_summary.csv", index=False)

    LOGGER.info(
        "Done. Ready accounts=%s ready contacts=%s suppressions=%s",
        len(accounts_all),
        len(contacts_all),
        len(suppressions),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

