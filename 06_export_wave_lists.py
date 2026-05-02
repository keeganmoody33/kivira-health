#!/usr/bin/env python3
"""
06_export_wave_lists.py

Export send-ready Wave 1 outbound lists for GA and NC from persona-mapped contacts + classified accounts.

Inputs (under ./output/):
- contacts_mapped_GA.csv
- contacts_mapped_NC.csv
- accounts_classified_GA.csv
- accounts_classified_NC.csv
- account_buying_committee_summary.csv

Outputs (under ./output/):
- wave1_accounts_GA.csv
- wave1_accounts_NC.csv
- wave1_contacts_GA.csv
- wave1_contacts_NC.csv
- wave1_accounts_all.csv
- wave1_contacts_all.csv
- wave1_review_queue.csv
- wave1_excluded_accounts.csv
- wave1_summary_by_state.csv

No new scraping, no inferred emails, no paid enrichment.
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pandas as pd

from tam_builder.pilot_filters import resolve_output_dir
from dateutil.parser import isoparse


LOGGER = logging.getLogger("kivira.wave1")


ACCOUNT_COLUMNS: List[str] = [
    "account_id",
    "org_name",
    "parent_org_id",
    "primary_state",
    "subtier_primary",
    "subtier_secondary_tags",
    "entity_type",
    "website",
    "phone_main",
    "wave_priority",
    "wave_status",
    "wave_reason",
    "primary_contact_id",
    "primary_contact_name",
    "primary_contact_title",
    "primary_contact_role",
    "backup_contact_id",
    "backup_contact_name",
    "backup_contact_title",
    "backup_contact_role",
    "economic_buyer_id",
    "economic_buyer_name",
    "economic_buyer_title",
    "technical_gatekeeper_id",
    "technical_gatekeeper_name",
    "technical_gatekeeper_title",
    "bh_quality_contact_id",
    "bh_quality_contact_name",
    "bh_quality_contact_title",
    "committee_coverage_score",
    "contactability_score",
    "account_readiness_score",
    "linkedin_company_url",
    "evidence_notes",
    "review_flag",
    "review_reason",
    "last_verified_at",
]


CONTACT_COLUMNS: List[str] = [
    "contact_id",
    "account_id",
    "org_name",
    "primary_state",
    "subtier_primary",
    "person_name",
    "job_title",
    "persona_role_primary",
    "persona_role_secondary",
    "outreach_sequence_stage",
    "buying_committee_fit_score",
    "demo_bookable_flag",
    "wave_1_eligible_flag",
    "preferred_contact_flag",
    "backup_contact_flag",
    "email",
    "phone_direct",
    "phone_main",
    "linkedin_profile_url",
    "source_url",
    "review_flag",
    "review_reason",
    "evidence_notes",
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


def safe_int(value: Any) -> Optional[int]:
    try:
        s = str(value or "").strip()
        if not s:
            return None
        return int(float(s))
    except Exception:
        return None


def as_bool_str(v: bool) -> str:
    return "true" if v else "false"


@dataclass(frozen=True)
class Floors:
    pcp_1a: int = 5
    pcp_1b: int = 3
    sites_1a: int = 2
    pcp_3a: int = 50
    sites_3a: int = 3


def compute_contactability_score(contacts: pd.DataFrame) -> float:
    """
    0..1 based on presence of direct email/phone on primary/backup candidates.
    """
    if contacts.empty:
        return 0.0
    has_email = (contacts["email"].astype(str).str.strip() != "").any()
    has_phone = ((contacts["phone_direct"].astype(str).str.strip() != "") | (contacts["phone_main"].astype(str).str.strip() != "")).any()
    has_linkedin = (contacts["linkedin_profile_url"].astype(str).str.strip() != "").any()
    score = 0.0
    score += 0.55 if has_email else 0.0
    score += 0.35 if has_phone else 0.0
    score += 0.10 if has_linkedin else 0.0
    return min(1.0, score)


def _is_demo_bookable(v: Any) -> bool:
    return str(v or "").strip().lower() in {"true", "1", "yes"}


def _fit(v: Any) -> float:
    return safe_float(v)


def _is_bad_primary_title(title: str) -> bool:
    t = (title or "").lower()
    return any(k in t for k in ["media", "press", "investor relations", "careers", "recruit", "marketing inbox", "info@"])


def select_primary_contact(contacts: pd.DataFrame, subtier: str) -> Tuple[Optional[pd.Series], str]:
    """
    Primary-contact selection rules:
    - Prefer Operational Owner; else Clinical Champion
    - For small 1B, allow Economic Buyer (owner) as primary
    - Require demo_bookable true, avoid bad titles
    """
    if contacts.empty:
        return None, "No contacts for account"

    c = contacts.copy()
    c["fit_num"] = c["buying_committee_fit_score"].apply(_fit)
    c["demo_ok"] = c["demo_bookable_flag"].apply(_is_demo_bookable)
    c = c[c["demo_ok"]].copy()
    if c.empty:
        return None, "No demo-bookable contacts"

    st = (subtier or "").strip().upper()

    def role_rank(role: str) -> int:
        if role == ROLE_OPERATIONAL_OWNER:
            return 1
        if role == ROLE_CLINICAL_CHAMPION:
            return 2
        if role == ROLE_ECONOMIC_BUYER:
            return 3 if st == "1B" else 4
        if role == ROLE_TECH_GATEKEEPER:
            return 4
        if role == ROLE_BH_QUALITY:
            return 5
        return 9

    c["role_rank"] = c["persona_role_primary"].astype(str).apply(role_rank)
    c = c.sort_values(["role_rank", "fit_num"], ascending=[True, False])

    for _, r in c.iterrows():
        if _is_bad_primary_title(str(r.get("job_title") or "")):
            continue
        return r, f"Selected primary by role preference ({r.get('persona_role_primary')}) and fit"

    return None, "Only low-quality/generic primary titles found"


def select_backup_contact(contacts: pd.DataFrame, primary_contact_id: str) -> Tuple[Optional[pd.Series], str]:
    if contacts.empty:
        return None, "No contacts"
    c = contacts.copy()
    c = c[c["contact_id"].astype(str) != str(primary_contact_id)].copy()
    c["fit_num"] = c["buying_committee_fit_score"].apply(_fit)
    c["demo_ok"] = c["demo_bookable_flag"].apply(_is_demo_bookable)
    c = c[c["demo_ok"]].copy()
    if c.empty:
        return None, "No backup demo-bookable contacts"
    c = c.sort_values(["fit_num"], ascending=[False])
    for _, r in c.iterrows():
        if _is_bad_primary_title(str(r.get("job_title") or "")):
            continue
        return r, "Selected backup as next-best demo-bookable contact"
    return None, "Only low-quality backup titles found"


def compute_account_readiness_score(
    committee_coverage_score: float,
    contactability_score: float,
    primary_fit: float,
    subtier: str,
    classification_confidence: float,
) -> float:
    """
    0..1 readiness: committee + contactability + primary quality + subtier attractiveness + classification confidence.
    """
    st = (subtier or "").strip().upper()
    subtier_bonus = 0.0
    if st in {"1C", "1A"}:
        subtier_bonus = 0.05
    if st in {"3C"}:
        subtier_bonus = 0.03

    score = 0.45 * committee_coverage_score + 0.35 * contactability_score + 0.15 * primary_fit + 0.05 * classification_confidence + subtier_bonus
    return max(0.0, min(1.0, score))


def assign_wave_status(
    *,
    excluded: bool,
    readiness: float,
    has_primary: bool,
    classification_status: str,
    classification_confidence: float,
    readiness_ready_threshold: float = 0.62,
) -> Tuple[str, str]:
    ready_thr = float(readiness_ready_threshold)
    if excluded:
        return "exclude", "Exclude: upstream exclusion"
    if str(classification_status or "").strip().lower() == "excluded":
        return "exclude", "Exclude: classification status excluded"
    if classification_confidence and classification_confidence < 0.50:
        return "review", "Review: weak or ambiguous account classification"
    if not has_primary and readiness >= 0.55:
        return "review", "Review: strong account but no valid primary contact"
    if readiness >= ready_thr and has_primary:
        return "ready", "Ready: sufficient readiness and primary contact"
    if readiness >= 0.45:
        return "review", "Review: partial readiness; needs more contacts or validation"
    return "exclude", "Exclude: below readiness threshold and/or no viable contact path"


def _size_floor_ok(
    acct: Dict[str, Any],
    floors: Floors,
    *,
    skip_1a_size_floor: bool = False,
) -> Tuple[bool, str]:
    st = str(acct.get("subtier_primary") or "").strip().upper()
    pcp = safe_int(acct.get("pcp_count_est"))
    sites = safe_int(acct.get("site_count_est"))
    if st == "1A":
        if skip_1a_size_floor:
            return True, ""
        if pcp is not None and pcp < floors.pcp_1a and (sites is None or sites < floors.sites_1a):
            return False, "Below 1A size floor (PCPs/sites)"
    if st == "1B":
        if pcp is not None and pcp < floors.pcp_1b:
            return False, "Below 1B size floor (PCPs)"
    if st == "3A":
        if pcp is not None and pcp < floors.pcp_3a and (sites is None or sites < floors.sites_3a):
            return False, "Below 3A size floor (PCPs/sites)"
    return True, ""


def _wave_priority(subtier: str, readiness: float) -> int:
    st = (subtier or "").strip().upper()
    base = 3
    if st == "1C":
        base = 1
    elif st == "1A":
        base = 2
    elif st == "1B":
        base = 3
    elif st == "2A":
        base = 3
    elif st.startswith("3"):
        base = 4
    # readiness nudges within bucket
    if readiness >= 0.75:
        return max(1, base - 1)
    return base


def write_research_queue_contacts(
    review_accounts: pd.DataFrame,
    mapped_contacts: pd.DataFrame,
    out_path: Path,
) -> int:
    """
    Contacts for accounts in wave review with at least one of email / phone / LinkedIn on the mapped row.
    Human-in-the-loop list separate from send-ready Wave 1.
    """
    if review_accounts.empty or mapped_contacts.empty:
        pd.DataFrame(columns=CONTACT_COLUMNS).to_csv(out_path, index=False)
        return 0
    rids = {str(x).strip() for x in review_accounts["account_id"].astype(str).tolist() if str(x).strip()}
    mc = mapped_contacts[mapped_contacts["account_id"].astype(str).str.strip().isin(rids)].copy()
    if mc.empty:
        pd.DataFrame(columns=CONTACT_COLUMNS).to_csv(out_path, index=False)
        return 0

    def _has_channel(row: pd.Series) -> bool:
        if str(row.get("email") or "").strip():
            return True
        if str(row.get("phone_direct") or "").strip() or str(row.get("phone_main") or "").strip():
            return True
        if str(row.get("linkedin_profile_url") or "").strip():
            return True
        return False

    mc = mc[mc.apply(_has_channel, axis=1)]
    mc = _ensure_cols(mc, CONTACT_COLUMNS)[CONTACT_COLUMNS]
    mc.to_csv(out_path, index=False)
    return len(mc)


def build_state_summary(accounts_df: pd.DataFrame) -> pd.DataFrame:
    if accounts_df.empty:
        return pd.DataFrame(
            columns=[
                "state",
                "subtier_primary",
                "total_accounts",
                "ready_accounts",
                "review_accounts",
                "excluded_accounts",
                "accounts_with_primary_contact",
                "accounts_with_backup_contact",
                "accounts_with_economic_buyer",
                "avg_committee_coverage_score",
                "avg_account_readiness_score",
                "last_verified_at",
            ]
        )

    def b(v: Any) -> bool:
        return str(v or "").strip().lower() in {"true", "1", "yes"}

    tmp = accounts_df.copy()
    tmp["state"] = tmp["primary_state"].astype(str).str.upper()
    tmp["subtier_primary"] = tmp["subtier_primary"].astype(str)
    tmp["wave_status"] = tmp["wave_status"].astype(str)

    def count_where(df: pd.DataFrame, mask: pd.Series) -> int:
        try:
            return int(mask.sum())
        except Exception:
            return 0

    rows: List[Dict[str, Any]] = []
    for (st, subtier), g in tmp.groupby(["state", "subtier_primary"], dropna=False):
        total = len(g)
        ready = (g["wave_status"] == "ready").sum()
        review = (g["wave_status"] == "review").sum()
        excl = (g["wave_status"] == "exclude").sum()
        with_primary = (g["primary_contact_id"].astype(str).str.strip() != "").sum()
        with_backup = (g["backup_contact_id"].astype(str).str.strip() != "").sum()
        with_eb = (g["economic_buyer_id"].astype(str).str.strip() != "").sum()
        avg_cov = g["committee_coverage_score"].apply(safe_float).mean() if total else 0.0
        avg_ready = g["account_readiness_score"].apply(safe_float).mean() if total else 0.0
        rows.append(
            {
                "state": st,
                "subtier_primary": subtier,
                "total_accounts": int(total),
                "ready_accounts": int(ready),
                "review_accounts": int(review),
                "excluded_accounts": int(excl),
                "accounts_with_primary_contact": int(with_primary),
                "accounts_with_backup_contact": int(with_backup),
                "accounts_with_economic_buyer": int(with_eb),
                "avg_committee_coverage_score": f"{avg_cov:.2f}",
                "avg_account_readiness_score": f"{avg_ready:.2f}",
                "last_verified_at": utc_now_iso(),
            }
        )
    return pd.DataFrame(rows)


def _ensure_cols(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df


def export_wave_for_state(
    state: str,
    contacts_df: pd.DataFrame,
    accounts_df: pd.DataFrame,
    committee_df: pd.DataFrame,
    floors: Floors,
    *,
    readiness_ready_threshold: float = 0.62,
    skip_1a_size_floor: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Returns: (wave_accounts, wave_contacts, review_queue, excluded_accounts)
    """
    st = state.strip().upper()

    a = accounts_df.copy()
    a = a[a["primary_state"].astype(str).str.upper() == st].copy()
    c = contacts_df.copy()
    c = c[c["primary_state"].astype(str).str.upper() == st].copy()

    a = _ensure_cols(
        a,
        [
            "account_id",
            "org_name",
            "parent_org_id",
            "primary_state",
            "subtier_primary",
            "subtier_secondary_tags",
            "entity_type",
            "website",
            "phone_main",
            "classification_status",
            "classification_confidence",
            "pcp_count_est",
            "site_count_est",
            "evidence_urls",
        ],
    )
    c = _ensure_cols(
        c,
        [
            "contact_id",
            "account_id",
            "org_name",
            "primary_state",
            "subtier_primary",
            "person_name",
            "job_title",
            "persona_role_primary",
            "persona_role_secondary",
            "outreach_sequence_stage",
            "buying_committee_fit_score",
            "demo_bookable_flag",
            "wave_1_eligible_flag",
            "email",
            "phone_direct",
            "phone_main",
            "linkedin_profile_url",
            "source_url",
            "review_flag",
            "review_reason",
            "evidence_notes",
            "last_verified_at",
            "linkedin_company_url",
        ],
    )

    committee_df = _ensure_cols(
        committee_df,
        ["account_id", "committee_coverage_score", "committee_gap_notes", "last_verified_at"],
    )
    committee_idx = {str(r["account_id"]): r for r in committee_df.to_dict(orient="records") if str(r.get("account_id") or "").strip()}

    # Parent dedupe: keep best readiness per parent_org_id where present
    account_rows: List[Dict[str, Any]] = []
    review_rows: List[Dict[str, Any]] = []
    excluded_rows: List[Dict[str, Any]] = []
    selected_by_parent: Dict[str, Tuple[str, float]] = {}

    for acct in a.to_dict(orient="records"):
        account_id = str(acct.get("account_id") or "").strip()
        org_name = str(acct.get("org_name") or "").strip()
        parent_org_id = str(acct.get("parent_org_id") or "").strip()
        subtier = str(acct.get("subtier_primary") or "").strip().upper()

        contacts = c[c["account_id"].astype(str) == account_id].copy()
        committee = committee_idx.get(account_id, {})
        committee_cov = safe_float(committee.get("committee_coverage_score"))
        committee_gap_notes = str(committee.get("committee_gap_notes") or "")

        # Apply size floors if possible
        size_ok, size_reason = _size_floor_ok(acct, floors, skip_1a_size_floor=skip_1a_size_floor)

        # Primary/backup selection
        primary, primary_reason = select_primary_contact(contacts, subtier)
        primary_fit = _fit(primary.get("buying_committee_fit_score")) if primary is not None else 0.0
        backup, backup_reason = (None, "")
        if primary is not None:
            backup, backup_reason = select_backup_contact(contacts, str(primary.get("contact_id") or ""))

        # Role-specific picks
        def best_for(role: str) -> Optional[pd.Series]:
            cc = contacts.copy()
            cc["fit_num"] = cc["buying_committee_fit_score"].apply(_fit)
            cc = cc[cc["demo_bookable_flag"].apply(_is_demo_bookable)].copy()
            cc = cc[cc["persona_role_primary"].astype(str) == role].copy()
            if cc.empty:
                return None
            cc = cc.sort_values("fit_num", ascending=False)
            return cc.iloc[0]

        eb = best_for(ROLE_ECONOMIC_BUYER)
        tg = best_for(ROLE_TECH_GATEKEEPER)
        bq = best_for(ROLE_BH_QUALITY)

        contactability = compute_contactability_score(contacts[contacts["demo_bookable_flag"].apply(_is_demo_bookable)].copy())
        class_conf = safe_float(acct.get("classification_confidence"))
        readiness = compute_account_readiness_score(committee_cov, contactability, primary_fit, subtier, class_conf)

        excluded = (not size_ok) or (str(acct.get("classification_status") or "").strip().lower() == "excluded")
        if not size_ok:
            wave_status, wave_reason = "exclude", f"Exclude: {size_reason}"
        else:
            wave_status, wave_reason = assign_wave_status(
                excluded=False,
                readiness=readiness,
                has_primary=primary is not None,
                classification_status=str(acct.get("classification_status") or ""),
                classification_confidence=class_conf,
                readiness_ready_threshold=readiness_ready_threshold,
            )

        # Parent dedupe / logo conflicts
        if parent_org_id:
            already = selected_by_parent.get(parent_org_id)
            if already and already[0] != account_id:
                # If current is better, demote previous to exclude; else exclude current.
                if readiness > already[1]:
                    selected_by_parent[parent_org_id] = (account_id, readiness)
                    # mark current as candidate, but we must demote previous later; easiest: review_flag for both and exclude the lower in a second pass
                else:
                    wave_status = "exclude"
                    wave_reason = "Exclude: duplicate child logo under already-selected parent"
            else:
                selected_by_parent[parent_org_id] = (account_id, readiness)

        wave_priority = _wave_priority(subtier, readiness)

        linkedin_company_url = ""
        if not contacts.empty:
            # prefer any company url found from discovery
            vals = [v for v in contacts["linkedin_company_url"].astype(str).tolist() if v.strip()]
            linkedin_company_url = vals[0] if vals else ""

        review_flag = wave_status == "review"
        review_reason = ""
        if review_flag:
            if primary is None:
                review_reason = "No primary contact selected; add operator/clinical champion"
            elif committee_cov < 0.40:
                review_reason = "Low committee coverage; add economic/tech/BH contacts"
            else:
                review_reason = committee_gap_notes or "Needs validation"

        evidence_notes = []
        if wave_status == "ready":
            evidence_notes.append("Ready for Wave 1 outreach")
        if primary is not None:
            evidence_notes.append(f"Primary: {primary.get('persona_role_primary')} ({primary_fit:.2f})")
        if eb is not None:
            evidence_notes.append("Economic Buyer identified")
        if tg is not None:
            evidence_notes.append("Technical Gatekeeper identified")
        if bq is not None:
            evidence_notes.append("BH/Quality Influencer identified")

        last_verified_at = parse_iso_or_now(acct.get("last_verified_at"))

        row: Dict[str, Any] = {c: "" for c in ACCOUNT_COLUMNS}
        row.update(
            {
                "account_id": account_id,
                "org_name": org_name,
                "parent_org_id": parent_org_id,
                "primary_state": st,
                "subtier_primary": subtier,
                "subtier_secondary_tags": str(acct.get("subtier_secondary_tags") or ""),
                "entity_type": str(acct.get("entity_type") or ""),
                "website": str(acct.get("website") or ""),
                "phone_main": str(acct.get("phone_main") or ""),
                "wave_priority": str(wave_priority),
                "wave_status": wave_status,
                "wave_reason": wave_reason,
                "primary_contact_id": str(primary.get("contact_id") or "") if primary is not None else "",
                "primary_contact_name": str(primary.get("person_name") or "") if primary is not None else "",
                "primary_contact_title": str(primary.get("job_title") or "") if primary is not None else "",
                "primary_contact_role": str(primary.get("persona_role_primary") or "") if primary is not None else "",
                "backup_contact_id": str(backup.get("contact_id") or "") if backup is not None else "",
                "backup_contact_name": str(backup.get("person_name") or "") if backup is not None else "",
                "backup_contact_title": str(backup.get("job_title") or "") if backup is not None else "",
                "backup_contact_role": str(backup.get("persona_role_primary") or "") if backup is not None else "",
                "economic_buyer_id": str(eb.get("contact_id") or "") if eb is not None else "",
                "economic_buyer_name": str(eb.get("person_name") or "") if eb is not None else "",
                "economic_buyer_title": str(eb.get("job_title") or "") if eb is not None else "",
                "technical_gatekeeper_id": str(tg.get("contact_id") or "") if tg is not None else "",
                "technical_gatekeeper_name": str(tg.get("person_name") or "") if tg is not None else "",
                "technical_gatekeeper_title": str(tg.get("job_title") or "") if tg is not None else "",
                "bh_quality_contact_id": str(bq.get("contact_id") or "") if bq is not None else "",
                "bh_quality_contact_name": str(bq.get("person_name") or "") if bq is not None else "",
                "bh_quality_contact_title": str(bq.get("job_title") or "") if bq is not None else "",
                "committee_coverage_score": f"{committee_cov:.2f}",
                "contactability_score": f"{contactability:.2f}",
                "account_readiness_score": f"{readiness:.2f}",
                "linkedin_company_url": linkedin_company_url,
                "evidence_notes": " | ".join(evidence_notes),
                "review_flag": as_bool_str(review_flag),
                "review_reason": review_reason,
                "last_verified_at": last_verified_at,
            }
        )

        if wave_status == "exclude":
            excluded_rows.append(row)
        elif wave_status == "review":
            review_rows.append(row)
            account_rows.append(row)
        else:
            account_rows.append(row)

    wave_accounts = pd.DataFrame(account_rows)
    wave_accounts = _ensure_cols(wave_accounts, ACCOUNT_COLUMNS)[ACCOUNT_COLUMNS]
    excluded_accounts = pd.DataFrame(excluded_rows)
    excluded_accounts = _ensure_cols(excluded_accounts, ACCOUNT_COLUMNS)[ACCOUNT_COLUMNS]
    review_queue = pd.DataFrame(review_rows)
    review_queue = _ensure_cols(review_queue, ACCOUNT_COLUMNS)[ACCOUNT_COLUMNS]

    # Wave contacts: include selected contacts, flagged
    selected_ids: Dict[str, Dict[str, str]] = {}
    for r in account_rows:
        aid = str(r.get("account_id") or "")
        selected_ids[aid] = {
            "primary": str(r.get("primary_contact_id") or ""),
            "backup": str(r.get("backup_contact_id") or ""),
            "eb": str(r.get("economic_buyer_id") or ""),
            "tg": str(r.get("technical_gatekeeper_id") or ""),
            "bq": str(r.get("bh_quality_contact_id") or ""),
        }

    contact_rows: List[Dict[str, Any]] = []
    for aid, ids in selected_ids.items():
        wanted = {v for v in ids.values() if v}
        if not wanted:
            continue
        subset = c[c["account_id"].astype(str) == aid].copy()
        subset = subset[subset["contact_id"].astype(str).isin(list(wanted))].copy()
        for _, rr in subset.iterrows():
            cid = str(rr.get("contact_id") or "")
            out = {c2: "" for c2 in CONTACT_COLUMNS}
            out.update({k: str(rr.get(k) or "") for k in CONTACT_COLUMNS if k in rr.index})
            out["preferred_contact_flag"] = as_bool_str(cid == ids.get("primary"))
            out["backup_contact_flag"] = as_bool_str(cid == ids.get("backup"))
            out["last_verified_at"] = parse_iso_or_now(rr.get("last_verified_at"))
            contact_rows.append(out)

    wave_contacts = pd.DataFrame(contact_rows).drop_duplicates(subset=["contact_id", "account_id"])
    wave_contacts = _ensure_cols(wave_contacts, CONTACT_COLUMNS)[CONTACT_COLUMNS]

    return wave_accounts, wave_contacts, review_queue, excluded_accounts


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Export Wave 1 outbound lists for GA/NC.")
    p.add_argument("--base-dir", default=".", help="Base directory containing output/.")
    p.add_argument("--states", default="GA,NC", help="Comma-separated states to export (default GA,NC).")
    p.add_argument("--log-level", default="INFO", help="Logging level.")
    p.add_argument(
        "--output-subdir",
        default="",
        help="Read/write under output/<subdir>/ (e.g. pilot).",
    )
    p.add_argument(
        "--readiness-ready-threshold",
        type=float,
        default=0.62,
        help="Minimum account_readiness score for wave_status=ready (pilot: try 0.55).",
    )
    p.add_argument(
        "--skip-1a-size-floor",
        action="store_true",
        help="Do not exclude 1A accounts on PCP/site count floor (use when estimates are sparse).",
    )
    p.add_argument(
        "--export-research-queue-contacts",
        action="store_true",
        help="Write research_queue_contacts_<ST>.csv for review accounts with any email/phone/LinkedIn.",
    )
    args = p.parse_args(argv)

    logging.basicConfig(level=getattr(logging, str(args.log_level).upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s - %(message)s")

    base_dir = Path(args.base_dir).expanduser().resolve()
    out_dir = resolve_output_dir(base_dir, str(args.output_subdir or ""))

    floors = Floors()
    states = [s.strip().upper() for s in str(args.states).split(",") if s.strip()]

    # Load shared inputs
    committee_path = out_dir / "account_buying_committee_summary.csv"
    committee_df = pd.read_csv(committee_path, dtype=str).fillna("") if committee_path.exists() else pd.DataFrame()

    all_accounts_out: List[pd.DataFrame] = []
    all_contacts_out: List[pd.DataFrame] = []
    all_reviews: List[pd.DataFrame] = []
    all_excl: List[pd.DataFrame] = []

    for st in states:
        contacts_path = out_dir / f"contacts_mapped_{st}.csv"
        accounts_path = out_dir / f"accounts_classified_{st}.csv"
        if not contacts_path.exists() or not accounts_path.exists():
            LOGGER.warning("Missing inputs for %s (skipping): %s %s", st, contacts_path, accounts_path)
            continue

        contacts_df = pd.read_csv(contacts_path, dtype=str).fillna("")
        accounts_df = pd.read_csv(accounts_path, dtype=str).fillna("")

        wave_accounts, wave_contacts, review_q, excluded = export_wave_for_state(
            st,
            contacts_df,
            accounts_df,
            committee_df,
            floors,
            readiness_ready_threshold=float(args.readiness_ready_threshold),
            skip_1a_size_floor=bool(args.skip_1a_size_floor),
        )

        wave_accounts.to_csv(out_dir / f"wave1_accounts_{st}.csv", index=False)
        wave_contacts.to_csv(out_dir / f"wave1_contacts_{st}.csv", index=False)

        if bool(args.export_research_queue_contacts):
            n_rq = write_research_queue_contacts(review_q, contacts_df, out_dir / f"research_queue_contacts_{st}.csv")
            LOGGER.info("Research queue contacts %s: %s rows", st, n_rq)

        all_accounts_out.append(wave_accounts)
        all_contacts_out.append(wave_contacts)
        all_reviews.append(review_q)
        all_excl.append(excluded)

    accounts_all = pd.concat(all_accounts_out, ignore_index=True) if all_accounts_out else pd.DataFrame(columns=ACCOUNT_COLUMNS)
    contacts_all = pd.concat(all_contacts_out, ignore_index=True) if all_contacts_out else pd.DataFrame(columns=CONTACT_COLUMNS)
    reviews_all = pd.concat(all_reviews, ignore_index=True) if all_reviews else pd.DataFrame(columns=ACCOUNT_COLUMNS)
    excl_all = pd.concat(all_excl, ignore_index=True) if all_excl else pd.DataFrame(columns=ACCOUNT_COLUMNS)

    accounts_all = _ensure_cols(accounts_all, ACCOUNT_COLUMNS)[ACCOUNT_COLUMNS]
    contacts_all = _ensure_cols(contacts_all, CONTACT_COLUMNS)[CONTACT_COLUMNS]
    reviews_all = _ensure_cols(reviews_all, ACCOUNT_COLUMNS)[ACCOUNT_COLUMNS]
    excl_all = _ensure_cols(excl_all, ACCOUNT_COLUMNS)[ACCOUNT_COLUMNS]

    accounts_all.to_csv(out_dir / "wave1_accounts_all.csv", index=False)
    contacts_all.to_csv(out_dir / "wave1_contacts_all.csv", index=False)
    reviews_all.to_csv(out_dir / "wave1_review_queue.csv", index=False)
    excl_all.to_csv(out_dir / "wave1_excluded_accounts.csv", index=False)

    summary_df = build_state_summary(accounts_all)
    summary_df.to_csv(out_dir / "wave1_summary_by_state.csv", index=False)

    LOGGER.info(
        "Done. Accounts=%s Contacts=%s Review=%s Excluded=%s",
        len(accounts_all),
        len(contacts_all),
        len(reviews_all),
        len(excl_all),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

