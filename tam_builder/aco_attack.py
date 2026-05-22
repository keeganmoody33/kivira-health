"""Tier 2A ACO attack-list logic: CMS org ingest, fit tiers, exclusions."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.request import Request, urlopen

DEFAULT_MSSP_ORGS_URL = (
    "https://data.cms.gov/sites/default/files/2026-04/"
    "358ddf60-c203-41ef-a0c6-a62a79f466ee/"
    "PY2026_Medicare_Shared_Savings_Program_Organizations.csv"
)

HOSPITAL_ONLY_RE = re.compile(
    r"\b(HOSPITAL|MEDICAL CENTER|HEALTH SYSTEM)\b",
    re.IGNORECASE,
)
PCP_NETWORK_SIGNAL_RE = re.compile(
    r"\b(PHYSICIAN|PHYSICIANS|PRIMARY CARE|MEDICAL GROUP|IPA|CLINIC|"
    r"HEALTH PARTNERS|ACO)\b",
    re.IGNORECASE,
)
ADMIN_SHELL_RE = re.compile(
    r"\b(HOLDING|ADMINISTRATIVE|CONSULTATION AND MANAGEMENT|"
    r"MANAGEMENT LLC|MANAGEMENT COMPANY)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AcoOrgRow:
    aco_id: str
    aco_name: str
    state: str
    agreement_period_num: int
    enhanced_track: bool
    basic_track: bool
    basic_track_level: str
    exec_name: str
    exec_email: str
    exec_phone: str
    medical_director_name: str
    value_based_track: str
    pc_flex: bool
    fit_tier: str
    exclude_reason: str = ""

    @property
    def has_cms_contact(self) -> bool:
        return bool((self.exec_name or "").strip() and (self.exec_email or "").strip())


def _http_get_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "kivira-aco-attack/1.0"})
    with urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8-sig", errors="replace")


def _norm_key(row: dict[str, str], *candidates: str) -> str:
    lower = {k.lower(): v for k, v in row.items()}
    for c in candidates:
        if c.lower() in lower:
            return (lower[c.lower()] or "").strip()
    return ""


def _truthy_flag(value: str) -> bool:
    v = (value or "").strip().lower()
    return v in {"1", "y", "yes", "true", "t"}


def _parse_period(value: str) -> int:
    if not value:
        return 0
    try:
        return int(float(value.strip()))
    except ValueError:
        return 0


def classify_fit_tier(enhanced: bool, period: int, reach: bool = False) -> str:
    if reach:
        return "HIGH"
    if enhanced and period >= 3:
        return "HIGH"
    if enhanced or period == 2:
        return "MEDIUM"
    if period == 1:
        return "LOWER"
    return "MEDIUM"


def exclusion_reason(name: str) -> str:
    n = (name or "").strip()
    if not n:
        return "missing_name"
    if ADMIN_SHELL_RE.search(n) and not PCP_NETWORK_SIGNAL_RE.search(n):
        return "admin_shell"
    if HOSPITAL_ONLY_RE.search(n) and not PCP_NETWORK_SIGNAL_RE.search(n):
        return "hospital_only"
    return ""


def parse_mssp_org_rows(csv_text: str) -> list[AcoOrgRow]:
    reader = csv.DictReader(io.StringIO(csv_text))
    by_name: dict[str, AcoOrgRow] = {}
    for raw in reader:
        name = _norm_key(raw, "aco_name", "ACO_Name")
        if not name:
            continue
        period = _parse_period(_norm_key(raw, "agreement_period_num", "Agreement_Period_Num"))
        enhanced = _truthy_flag(_norm_key(raw, "enhanced_track", "ENHANCED_Track"))
        basic = _truthy_flag(_norm_key(raw, "basic_track", "BASIC_Track"))
        pc_flex = _truthy_flag(_norm_key(raw, "pc_flex_agreement_status"))
        state = _norm_key(raw, "aco_service_area", "ACO_Service_Area")
        if "," in state:
            state = state.split(",")[0].strip()
        ex = exclusion_reason(name)
        fit = classify_fit_tier(enhanced, period)
        if pc_flex and fit != "HIGH":
            fit = "MEDIUM"
        row = AcoOrgRow(
            aco_id=_norm_key(raw, "aco_id", "ACO_ID"),
            aco_name=name,
            state=state,
            agreement_period_num=period,
            enhanced_track=enhanced,
            basic_track=basic,
            basic_track_level=_norm_key(raw, "basic_track_level", "BASIC_Track_Level"),
            exec_name=_norm_key(raw, "aco_exec_name", "ACO_Exec_Name"),
            exec_email=_norm_key(raw, "aco_exec_email", "ACO_Exec_Email"),
            exec_phone=_norm_key(raw, "aco_exec_phone", "ACO_Exec_Phone"),
            medical_director_name=_norm_key(
                raw, "aco_medical_director_name", "ACO_Medical_Director_Name"
            ),
            value_based_track="MSSP ACO",
            pc_flex=pc_flex,
            fit_tier=fit,
            exclude_reason=ex,
        )
        key = name.lower()
        prev = by_name.get(key)
        if prev is None or (fit == "HIGH" and prev.fit_tier != "HIGH"):
            by_name[key] = row
    return list(by_name.values())


def parse_reach_rows(csv_rows: Iterable[dict[str, str]]) -> list[AcoOrgRow]:
    out: list[AcoOrgRow] = []
    for raw in csv_rows:
        name = _norm_key(raw, "aco_name", "ACO Name", "Legal Business Name", "participant_name")
        if not name:
            continue
        state = _norm_key(raw, "state", "State", "States")
        if "," in state:
            state = state.split(",")[0].strip()
        ex = exclusion_reason(name)
        out.append(
            AcoOrgRow(
                aco_id=_norm_key(raw, "aco_id", "ACO_ID"),
                aco_name=name,
                state=state,
                agreement_period_num=3,
                enhanced_track=True,
                basic_track=False,
                basic_track_level="",
                exec_name=_norm_key(raw, "exec_name", "contact_name"),
                exec_email=_norm_key(raw, "exec_email", "contact_email"),
                exec_phone=_norm_key(raw, "exec_phone", "contact_phone"),
                medical_director_name="",
                value_based_track="ACO REACH",
                pc_flex=False,
                fit_tier="HIGH",
                exclude_reason=ex,
            )
        )
    return out


def load_mssp_orgs(*, csv_path: Path | None = None, url: str = DEFAULT_MSSP_ORGS_URL) -> list[AcoOrgRow]:
    if csv_path and csv_path.exists():
        text = csv_path.read_text(encoding="utf-8-sig")
    else:
        text = _http_get_text(url)
    return parse_mssp_org_rows(text)


def net_2a_orgs(
    mssp: list[AcoOrgRow],
    reach: list[AcoOrgRow] | None = None,
) -> list[AcoOrgRow]:
    """Merge REACH over MSSP; drop excluded rows."""
    merged: dict[str, AcoOrgRow] = {r.aco_name.lower(): r for r in mssp}
    for r in reach or []:
        key = r.aco_name.lower()
        if key not in merged or r.fit_tier == "HIGH":
            merged[key] = r
    return [r for r in merged.values() if not r.exclude_reason]


def to_csv_dict(row: AcoOrgRow) -> dict[str, str]:
    return {
        "aco_id": row.aco_id,
        "aco_name": row.aco_name,
        "state": row.state,
        "subtier_primary": "2A",
        "fit_tier": row.fit_tier,
        "agreement_period_num": str(row.agreement_period_num),
        "enhanced_track": "1" if row.enhanced_track else "0",
        "basic_track": "1" if row.basic_track else "0",
        "basic_track_level": row.basic_track_level,
        "value_based_track": row.value_based_track,
        "pc_flex": "1" if row.pc_flex else "0",
        "exec_name": row.exec_name,
        "exec_email": row.exec_email,
        "exec_phone": row.exec_phone,
        "medical_director_name": row.medical_director_name,
        "has_cms_contact": "true" if row.has_cms_contact else "false",
        "exclude_reason": row.exclude_reason,
        "primary_motion": "2A_entity",
        "tam_acv_usd": "120000",
    }


def write_attack_csv(path: Path, rows: list[AcoOrgRow]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(to_csv_dict(rows[0]).keys()) if rows else [
        "aco_id", "aco_name", "state", "subtier_primary", "fit_tier",
        "agreement_period_num", "enhanced_track", "basic_track", "basic_track_level",
        "value_based_track", "pc_flex", "exec_name", "exec_email", "exec_phone",
        "medical_director_name", "has_cms_contact", "exclude_reason",
        "primary_motion", "tam_acv_usd",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(to_csv_dict(row))
