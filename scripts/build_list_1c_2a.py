#!/usr/bin/env python3
"""Build Wave 1 raw account list for Tier 1C + Tier 2A.

This script produces a CSV that can be ingested by `tam_builder normalize-accounts`.

Design intent:
- Be useful immediately with *either* downloaded public files *or* manually prepared exports.
- Avoid hardcoding credentials; only uses public HTTP downloads.

Inputs (recommended):
- MSSP ACO participants export (CSV) OR a URL that directly serves a CSV.
- Optional ACO REACH participant list (CSV). The public source is a PDF; converting it to CSV is
  intentionally a manual step in v1.

Output:
- A raw accounts CSV with headers compatible with `tam_builder.constants.COLUMN_ALIASES`.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from urllib.request import Request, urlopen


DEFAULT_MSSP_PAGE_URL = (
    "https://data.cms.gov/medicare-shared-savings-program/"
    "accountable-care-organization-participants"
)
DEFAULT_REACH_PDF_URL = "https://www.cms.gov/priorities/innovation/files/aco-reach-py2026-participants.pdf"


RAW_HEADERS = [
    "Organization Name",
    "State Code",
    "Metro",
    "Organization Type",
    "Priority Personas",
    "Candidate Ceiling",
    "Internal Notes",
    "Source System",
    "Source ID",
    "Parent Org",
    "System Affiliation",
    "Value-Based Track",
    "Primary EHR",
    "Payer Mix",
    "Ambient AI Vendor",
    "BH Readiness",
    "Procurement Type",
    "Active Competitor",
    "Decision Makers",
    "Has Named Contact",
    "Contact Name",
    "Contact Title",
    "Contact Email",
]


@dataclass(frozen=True)
class InputRow:
    org_name: str
    state: str
    source: str
    source_id: str
    subtier: str
    value_based_track: str
    contact_name: str = ""
    contact_title: str = ""
    contact_email: str = ""


def _http_get_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "kivira-list-builder/1.0"})
    with urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _http_get_bytes(url: str) -> bytes:
    req = Request(url, headers={"User-Agent": "kivira-list-builder/1.0"})
    with urlopen(req, timeout=120) as resp:
        return resp.read()


def _looks_like_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
    except Exception:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _resolve_mssp_csv_url(mssp_page_url: str) -> str | None:
    """Best-effort: fetch the CMS dataset landing page and try to find a CSV download URL."""
    html = _http_get_text(mssp_page_url)
    # Heuristic: look for a direct CSV link.
    candidates = set(re.findall(r"https?://[^\"]+?\.csv", html, flags=re.IGNORECASE))
    if candidates:
        # Prefer data.cms.gov hosted links if multiple.
        preferred = sorted(candidates, key=lambda u: ("data.cms.gov" not in u, len(u)))
        return preferred[0]
    return None


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader]


def _read_csv_rows_from_bytes(data: bytes) -> list[dict[str, str]]:
    text = data.decode("utf-8", errors="replace")
    with io.StringIO(text) as f:
        reader = csv.DictReader(f)
        return [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader]


def _stable_source_id(prefix: str, org_name: str, state: str) -> str:
    h = hashlib.sha256(f"{prefix}|{org_name}|{state}".encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{h}"


def parse_mssp_participants(rows: list[dict[str, str]]) -> list[InputRow]:
    """Parse a 'good enough' subset from whatever MSSP export the user provides.

    The CMS dataset fields vary by export. This parser uses multiple field-name fallbacks.
    """
    parsed: list[InputRow] = []
    for row in rows:
        aco_name = (
            row.get("aco_name")
            or row.get("ACO Name")
            or row.get("ACO_Name")  # PY2026 CMS public CSV header
            or row.get("Accountable Care Organization (ACO) Name")
            or row.get("accountable_care_organization_aco_name")
            or ""
        ).strip()
        # ACO_Service_Area in the PY2026 CSV holds a state code (or comma list).
        state = (
            row.get("state")
            or row.get("State")
            or row.get("aco_state")
            or row.get("ACO_Service_Area")
            or ""
        ).strip()
        contact_name = (
            row.get("aco_contact_name")
            or row.get("Contact Name")
            or row.get("primary_contact_name")
            or row.get("ACO_Exec_Name")  # PY2026 CMS exec contact
            or row.get("ACO_Public_Name")
            or ""
        ).strip()
        contact_email = (
            row.get("aco_contact_email")
            or row.get("Contact Email")
            or row.get("primary_contact_email")
            or row.get("ACO_Exec_Email")
            or row.get("ACO_Public_Email")
            or ""
        ).strip()
        contact_title = (
            row.get("aco_contact_title")
            or row.get("Contact Title")
            or row.get("primary_contact_title")
            or ""
        ).strip()
        # If contact came from ACO_Exec_*, default the title.
        if contact_name and not contact_title:
            if row.get("ACO_Exec_Name"):
                contact_title = "ACO Executive (per CMS public filing)"
            elif row.get("ACO_Public_Name"):
                contact_title = "ACO Public Contact (per CMS public filing)"
        if not aco_name:
            continue
        # Tier 2A rows.
        parsed.append(
            InputRow(
                org_name=aco_name,
                state=state,
                source="CMS_MSSP_ACO_PARTICIPANTS",
                source_id=_stable_source_id("MSSP", aco_name, state),
                subtier="2A",
                value_based_track="MSSP ACO",
                contact_name=contact_name,
                contact_title=contact_title,
                contact_email=contact_email,
            )
        )
    return parsed


# ---------------------------------------------------------------------------
# Tier 1C participant inclusion — TODO: Keegan, this is the meaningful decision
# ---------------------------------------------------------------------------
#
# The PY2026 MSSP CSV has ~15,293 unique participant orgs (Par_LBN). Real
# distribution from May 2026 inspection:
#   - ~4,477 look like medical groups (true 1C signal)
#   - ~1,480 look like hospitals (3A — should be excluded from 1C)
#   - ~  417 look like FQHCs / community health centers (1B per Kivira docs)
#   - ~9,034 are ambiguous (single-doc practices, specialty clinics, etc.)
#
# Three honest strategies — each shapes downstream HeyReach campaign size and
# message precision differently:
#
#   STRATEGY A — STRICT 1C (~3,000 accounts after dedup)
#   Keep only names with explicit medical-group keywords AND a primary-care
#   signal. Highest precision. Best for narrow CoCM messaging at PCP-flavored
#   groups. Drops the long tail of ambiguous single-doctor practices.
#
#   STRATEGY B — PERMISSIVE 1C (~12,000 accounts after dedup)
#   Keep everything except hospitals/medical-centers and FQHCs. High recall;
#   accept the noise of specialty clinics and let downstream Parallel/HeyReach
#   triage. Best when you have time to tune. Worst for first-shot precision.
#
#   STRATEGY C — PRIMARY-CARE-ANCHORED 1C (~2,500 accounts after dedup)
#   Hardest filter: must contain explicit primary-care language ("FAMILY",
#   "INTERNAL MEDICINE", "PRIMARY CARE", "FAMILY PHYSICIANS", etc.) AND must
#   not contain hospital/system noise. Tightest fit for CoCM wedge. Smallest
#   pool; some real 1C accounts get missed.
#
# When you implement is_likely_1c() below, pick a strategy (or hybrid) and
# return True if the org should be tagged as 1C. The framework around it
# (parsing, dedupe, output) is already wired — your 5-10 lines of business
# logic decide what flows into HeyReach.


HOSPITAL_NOISE_RE = re.compile(
    r"\b(HOSPITAL|MEDICAL CENTER|HEALTH SYSTEM|HEALTHCARE SYSTEM|UNIVERSITY|REGIONAL HEALTH|CLINIC HOSPITAL)\b",
    re.IGNORECASE,
)
GROUP_SIGNAL_RE = re.compile(
    r"\b(MEDICAL GROUP|MEDICAL ASSOCIATES|PHYSICIANS|FAMILY PRACTICE|FAMILY MEDICINE|"
    r"INTERNAL MEDICINE|PRIMARY CARE|FAMILY HEALTH|HEALTH PARTNERS|MEDICAL CLINIC|"
    r"FAMILY PHYSICIANS|MD PA|MD PC|FAMILY DOCTORS|IPA|INDEPENDENT PRACTICE)\b",
    re.IGNORECASE,
)
PRIMARY_CARE_ANCHOR_RE = re.compile(
    r"\b(FAMILY|INTERNAL MEDICINE|PRIMARY CARE|FAMILY PHYSICIANS|FAMILY DOCTORS|"
    r"GENERAL PRACTICE|FAMILY HEALTH|PRIMARY)\b",
    re.IGNORECASE,
)
FQHC_NOISE_RE = re.compile(
    r"\b(FQHC|COMMUNITY HEALTH CENTER|FEDERALLY QUALIFIED|HEALTH CENTER, INC)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Provider-strategy classifier (Keegan's three-bucket design, ported from JS)
# ---------------------------------------------------------------------------
#
# Each MSSP Par_LBN maps to ONE of three buckets:
#   - PCP_GROUP — primary-care-flavored, not specialty (clearest 1C signal)
#   - VBC_PROVIDER_GROUP — ACO / MSSP / VBC / IPA-flavored (Aledade-style 1C)
#   - MID_MARKET_PROVIDER_GROUP — catchall (no positive signal; treat as noise
#     for now — hospitals + specialty + single-doc practices land here)
#
# `INCLUDED_STRATEGIES` controls which buckets get tagged as 1C and loaded.
# Default: PCP_GROUP + VBC_PROVIDER_GROUP. Flip to include MID_MARKET if
# you want full recall (with the noise that comes with it).

class Strategy:
    PCP_GROUP = "PCP_GROUP"
    VBC_PROVIDER_GROUP = "VBC_PROVIDER_GROUP"
    MID_MARKET_PROVIDER_GROUP = "MID_MARKET_PROVIDER_GROUP"


INCLUDED_STRATEGIES = {Strategy.PCP_GROUP, Strategy.VBC_PROVIDER_GROUP}

# Ported faithfully from Keegan's JS draft. No word boundaries (matches his
# original); regexes operate on lower-cased name. If false positives appear
# (e.g. "ENT" matching "patient", "pain" matching "Spain"), tighten with \b.
PCP_RE = re.compile(
    r"(family medicine|internal medicine|primary care|pcp|fqhc|"
    r"community health|ambulatory|medical group|physician(s)? group)",
    re.IGNORECASE,
)
SPECIALTY_RE = re.compile(
    r"(cardio|ortho|derm|oncology|gastro|urology|ophthalm|ent|"
    r"neuro|pain|surgery|specialty)",
    re.IGNORECASE,
)
VBC_RE = re.compile(
    r"(aco|mssp|value[- ]based|vbc|clinically integrated|"
    r"population health|shared savings|risk|ipa|pho)",
    re.IGNORECASE,
)


def classify_provider_strategy(name: str) -> str:
    """Three-bucket classifier (Keegan's GTM rules)."""
    n = (name or "").strip().lower()
    if PCP_RE.search(n) and not SPECIALTY_RE.search(n):
        return Strategy.PCP_GROUP
    if VBC_RE.search(n):
        return Strategy.VBC_PROVIDER_GROUP
    return Strategy.MID_MARKET_PROVIDER_GROUP


def is_likely_1c(par_lbn: str) -> bool:
    """True if classifier puts this name in an INCLUDED_STRATEGIES bucket."""
    name = (par_lbn or "").strip()
    if not name:
        return False
    return classify_provider_strategy(name) in INCLUDED_STRATEGIES


def parse_mssp_participants_as_1c(rows: list[dict[str, str]]) -> list[InputRow]:
    """Pull Par_LBN rows tagged as Tier 1C using is_likely_1c() above.

    Each MSSP CSV row has both ACO_Name (2A — handled by the parser above)
    and Par_LBN (1C candidate — handled here). This function applies the
    user-defined inclusion filter and emits 1C InputRows.
    """
    parsed: list[InputRow] = []
    for row in rows:
        par_lbn = (row.get("Par_LBN") or row.get("par_lbn") or "").strip()
        if not par_lbn or not is_likely_1c(par_lbn):
            continue
        state = (
            row.get("ACO_Service_Area")
            or row.get("state")
            or row.get("State")
            or ""
        ).strip()
        # Take just the first state if it's a comma list (1C orgs are typically single-state).
        if "," in state:
            state = state.split(",")[0].strip()
        parsed.append(
            InputRow(
                org_name=par_lbn,
                state=state,
                source="CMS_MSSP_PAR_LBN",
                source_id=_stable_source_id("MSSP-PAR", par_lbn, state),
                subtier="1C",
                value_based_track="MSSP Participant",
            )
        )
    return parsed


def parse_reach_participants(rows: list[dict[str, str]]) -> list[InputRow]:
    """Parse ACO REACH participants from a user-provided CSV (v1)."""
    parsed: list[InputRow] = []
    for row in rows:
        name = (row.get("aco_name") or row.get("ACO Name") or row.get("Participant") or row.get("participant_name") or "").strip()
        state = (row.get("state") or row.get("State") or "").strip()
        if not name:
            continue
        parsed.append(
            InputRow(
                org_name=name,
                state=state,
                source="CMS_ACO_REACH_PARTICIPANTS",
                source_id=_stable_source_id("REACH", name, state),
                subtier="2A",
                value_based_track="ACO REACH",
            )
        )
    return parsed


def dedup_inputs(rows: Iterable[InputRow]) -> list[InputRow]:
    seen: set[tuple[str, str]] = set()
    out: list[InputRow] = []
    for r in rows:
        key = (r.org_name.lower().strip(), r.state.upper().strip())
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def to_raw_account_row(r: InputRow, candidate_ceiling: int) -> dict[str, str]:
    org_type = "aco_parent" if r.subtier == "2A" else "independent_group"
    notes = f"wave=1; subtier={r.subtier}; source={r.source}"
    return {
        "Organization Name": r.org_name,
        "State Code": r.state,
        "Metro": "",
        "Organization Type": org_type,
        "Priority Personas": "",
        "Candidate Ceiling": str(candidate_ceiling),
        "Internal Notes": notes,
        "Source System": "Public",
        "Source ID": r.source_id,
        "Parent Org": "",
        "System Affiliation": "",
        "Value-Based Track": r.value_based_track,
        "Primary EHR": "",
        "Payer Mix": "",
        "Ambient AI Vendor": "",
        "BH Readiness": "",
        "Procurement Type": "",
        "Active Competitor": "",
        "Decision Makers": "",
        "Has Named Contact": "true" if (r.contact_name or r.contact_email) else "false",
        "Contact Name": r.contact_name,
        "Contact Title": r.contact_title,
        "Contact Email": r.contact_email,
    }


def write_raw_accounts(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow({h: row.get(h, "") for h in RAW_HEADERS})


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Build Wave 1 list (1C + 2A).")
    p.add_argument("--out", default=str(Path("fixtures") / "wave1_raw_accounts.csv"))
    p.add_argument("--candidate-ceiling", type=int, default=220)

    p.add_argument("--mssp-csv", help="Path to downloaded CMS MSSP participant CSV.")
    p.add_argument("--mssp-url", help="Direct URL to a MSSP participant CSV.")
    p.add_argument("--mssp-page-url", default=DEFAULT_MSSP_PAGE_URL, help="CMS MSSP dataset landing page URL.")

    p.add_argument("--reach-csv", help="Optional: path to an ACO REACH participants CSV (manual conversion).")
    p.add_argument("--download-reach-pdf", action="store_true", help="Download the ACO REACH PDF to artifacts/ for manual conversion.")
    p.add_argument("--reach-pdf-url", default=DEFAULT_REACH_PDF_URL)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    out_path = Path(args.out)

    inputs: list[InputRow] = []

    mssp_rows: list[dict[str, str]] = []
    if args.mssp_csv:
        mssp_rows = _read_csv_rows(Path(args.mssp_csv))
    elif args.mssp_url:
        if not _looks_like_url(args.mssp_url):
            raise SystemExit("--mssp-url must be a valid http(s) URL")
        mssp_rows = _read_csv_rows_from_bytes(_http_get_bytes(args.mssp_url))
    else:
        # Best-effort download discovery from landing page.
        csv_url = _resolve_mssp_csv_url(args.mssp_page_url)
        if csv_url:
            mssp_rows = _read_csv_rows_from_bytes(_http_get_bytes(csv_url))
        else:
            print(
                "Could not auto-discover a MSSP CSV URL from the landing page.\n"
                "Provide --mssp-csv (recommended) or --mssp-url (direct CSV).",
                file=sys.stderr,
            )
            return 2

    inputs.extend(parse_mssp_participants(mssp_rows))
    # 1C participants — only emits rows once is_likely_1c() is implemented.
    inputs.extend(parse_mssp_participants_as_1c(mssp_rows))

    if args.reach_csv:
        reach_rows = _read_csv_rows(Path(args.reach_csv))
        inputs.extend(parse_reach_participants(reach_rows))
    elif args.download_reach_pdf:
        pdf_bytes = _http_get_bytes(args.reach_pdf_url)
        artifacts_dir = Path("artifacts")
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = artifacts_dir / "aco_reach_py2026_participants.pdf"
        pdf_path.write_bytes(pdf_bytes)
        print(f"Downloaded ACO REACH PDF to {pdf_path}", file=sys.stderr)

    inputs = dedup_inputs(inputs)

    raw_rows = [to_raw_account_row(r, candidate_ceiling=args.candidate_ceiling) for r in inputs]
    write_raw_accounts(out_path, raw_rows)
    print(f"Wrote {len(raw_rows)} rows to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

