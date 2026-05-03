#!/usr/bin/env python3
"""Build Wave 2 raw account list for Tier 1A (mid-market provider groups).

This is intentionally file-driven (not auto-downloading NPPES) because NPPES bulk downloads are large.
You download the monthly NPPES file and (optionally) the CMS Doctors & Clinicians export, then run this
script to filter/join and produce a `raw_accounts` CSV that the TAM builder can normalize.

Inputs:
- NPPES organizations file (CSV) containing Type 2 NPIs (full NPPES export or a pre-filtered subset).
- Optional: CMS Doctors & Clinicians National file export (CSV) with group practice PAC IDs / clinician NPIs.
- Optional: list of MSSP-affiliated TINs/NPIs for secondary tagging (CSV).
- Optional: NCQA BHI distinction list (manual CSV), since the free directory isn't bulk-downloadable.

Output:
- `fixtures/wave2_raw_accounts.csv` by default.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path


PRIMARY_CARE_TAXONOMY_CODES = {
    "207Q00000X",  # Family Medicine
    "207R00000X",  # Internal Medicine
    "207QA0505X",  # Adult Medicine
    "363L00000X",  # Nurse Practitioner, Primary Care
    "208D00000X",  # General Practice
    "208000000X",  # Pediatrics
}


# Hospital / IDN / academic / government patterns that pass the taxonomy + size
# gate but aren't 1A targets — they belong in 3A (health system) or 3B (IDN).
# Mirrors the noise filter pattern used in build_list_1c_2a.py. Disable with
# `--include-noise` if you want to see what's being dropped.
HOSPITAL_NOISE_RE = re.compile(
    r"\b("
    r"HOSPITAL|MEDICAL CENTER|HEALTH SYSTEM|HEALTHCARE SYSTEM|"
    r"REGIONAL HEALTH|HEALTH \& SERVICES|HEALTH AND SERVICES|"
    r"CLINIC HOSPITAL|HOSPITAL DISTRICT|HOSPITALS"
    r"|UNIVERSITY|BOARD OF REGENTS|SCHOOL OF MEDICINE"
    r"|COMMISSION|DEPARTMENT OF|BUREAU OF"
    r")\b",
    re.IGNORECASE,
)


def is_org_noise(org_name: str) -> bool:
    """True if the org name matches a hospital/IDN/academic/government pattern."""
    return bool(HOSPITAL_NOISE_RE.search(org_name or ""))


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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader]


def stream_csv(path: Path):
    """Yield one cleaned row dict at a time — use for large files (>1GB) to avoid OOM."""
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield {(k or "").strip(): (v or "").strip() for k, v in row.items()}


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow({h: row.get(h, "") for h in RAW_HEADERS})


def nppes_is_type2_org(row: dict[str, str]) -> bool:
    code = (row.get("Entity Type Code") or row.get("entity_type_code") or "").strip()
    return code == "2"


def nppes_state(row: dict[str, str]) -> str:
    return (
        row.get("Provider Business Practice Location Address State Name")
        or row.get("provider_business_practice_location_address_state_name")
        or row.get("State")
        or ""
    ).strip()


def nppes_org_name(row: dict[str, str]) -> str:
    return (
        row.get("Provider Organization Name (Legal Business Name)")
        or row.get("provider_organization_name_legal_business_name")
        or row.get("Organization Name")
        or row.get("org_name")
        or ""
    ).strip()


def nppes_taxonomy_codes(row: dict[str, str]) -> set[str]:
    # NPPES exports have multiple taxonomy slots; we check for any primary care taxonomy.
    codes: set[str] = set()
    for key, value in row.items():
        if "Healthcare Provider Taxonomy Code" in key or key.lower().endswith("taxonomy_code"):
            if value:
                codes.add(value.strip())
    return codes


def build_pcp_counts_from_cms_doctors(rows: list[dict[str, str]]) -> dict[str, int]:
    """Return map of group identifier -> PCP count (best-effort).

    CMS Doctors & Clinicians exports vary. We look for a 'group practice PAC ID' column if present,
    otherwise fall back to grouping by 'Organization legal name' if present.
    """
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        group_id = (
            row.get("Group Practice PAC ID")
            or row.get("group_practice_pac_id")
            or row.get("group_pac_id")
            or ""
        ).strip()
        if not group_id:
            group_id = (row.get("Organization legal name") or row.get("organization_legal_name") or "").strip()
        if not group_id:
            continue
        counts[group_id] += 1
    return dict(counts)


def aggregate_orgs_from_nppes(
    nppes_rows,
    state_filter: set[str] | None = None,
) -> tuple[dict[tuple[str, str], dict[str, object]], dict[str, int]]:
    """Single streaming pass — aggregate Type-2 NPIs to (org_name_upper, state) keys.

    Returns:
      org_data: map of (org_upper, state) -> {count, original_name, ao_last, ao_first}
      stats: dict of skip/total counters for visibility.
    """
    org_data: dict[tuple[str, str], dict[str, object]] = {}
    stats = {
        "total_seen": 0,
        "skipped_not_type2": 0,
        "skipped_state": 0,
        "skipped_no_primary_care": 0,
        "skipped_no_org_name": 0,
    }

    for row in nppes_rows:
        stats["total_seen"] += 1
        if stats["total_seen"] % 500_000 == 0:
            print(
                f"  {stats['total_seen']:,} NPPES rows scanned, "
                f"{len(org_data):,} orgs so far...",
                file=sys.stderr,
                flush=True,
            )

        if not nppes_is_type2_org(row):
            stats["skipped_not_type2"] += 1
            continue

        st = nppes_state(row).upper()
        if state_filter and st not in state_filter:
            stats["skipped_state"] += 1
            continue

        if not (nppes_taxonomy_codes(row) & PRIMARY_CARE_TAXONOMY_CODES):
            stats["skipped_no_primary_care"] += 1
            continue

        org_name = nppes_org_name(row)
        if not org_name:
            stats["skipped_no_org_name"] += 1
            continue

        key = (org_name.upper().strip(), st)
        if key not in org_data:
            org_data[key] = {
                "count": 0,
                "original_name": org_name,
                "ao_last": (row.get("Authorized Official Last Name") or "").strip(),
                "ao_first": (row.get("Authorized Official First Name") or "").strip(),
            }
        org_data[key]["count"] = int(org_data[key]["count"]) + 1  # type: ignore[arg-type]

    return org_data, stats


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Build Wave 2 list (1A mid-market PCP-heavy groups) from NPPES Type-2."
    )
    p.add_argument("--nppes-csv", required=True, help="Path to NPPES Type-2 CSV.")
    p.add_argument(
        "--out",
        default=str(Path("fixtures") / "wave2_1a_raw_accounts.csv"),
        help="Output CSV path.",
    )
    p.add_argument(
        "--states",
        help="Optional comma-separated list of 2-letter state codes to include.",
    )
    p.add_argument(
        "--min-org-npis",
        type=int,
        default=2,
        help="Min Type-2 NPIs per (org name, state) — proxy for multi-site (>=2 sites).",
    )
    p.add_argument(
        "--max-org-npis",
        type=int,
        default=30,
        help="Max Type-2 NPIs per (org name, state) — drops mega-chain noise.",
    )
    p.add_argument("--candidate-ceiling", type=int, default=150)
    p.add_argument(
        "--include-noise",
        action="store_true",
        help="Disable hospital/IDN/academic/govt noise filter (for debug only).",
    )
    args = p.parse_args(argv)

    nppes_path = Path(args.nppes_csv)
    state_filter: set[str] | None = None
    if args.states:
        state_filter = {s.strip().upper() for s in args.states.split(",") if s.strip()}

    # Pass 1 (streaming): aggregate by (org_name_upper, state). Counts Type-2 NPIs
    # that survive taxonomy + state filters. NPI-count is a multi-site proxy.
    org_data, stats = aggregate_orgs_from_nppes(stream_csv(nppes_path), state_filter)

    # Pass 2: size gate + noise filter — emit one row per (org, state) with
    # count in [min, max] AND not matching the hospital/IDN/academic/govt regex.
    out_rows: list[dict[str, str]] = []
    size_gate_dropped = 0
    noise_dropped = 0
    for (org_upper, st), data in org_data.items():
        count = int(data["count"])  # type: ignore[arg-type]
        if not (args.min_org_npis <= count <= args.max_org_npis):
            size_gate_dropped += 1
            continue
        if not args.include_noise and is_org_noise(str(data["original_name"])):
            noise_dropped += 1
            continue
        ao_part = f"{data['ao_last']} {data['ao_first']}".strip()
        notes = f"wave=2; subtier=1A; source=NPPES; npi_count={count}"
        if ao_part:
            notes += f"; ao={ao_part}"

        out_rows.append(
            {
                "Organization Name": str(data["original_name"]),
                "State Code": st,
                "Metro": "",
                "Organization Type": "independent_group",
                "Priority Personas": "",
                "Candidate Ceiling": str(args.candidate_ceiling),
                "Internal Notes": notes,
                "Source System": "Public",
                "Source ID": f"NPPES-{org_upper}|{st}",
                "Parent Org": "",
                "System Affiliation": "",
                "Value-Based Track": "",
                "Primary EHR": "",
                "Payer Mix": "",
                "Ambient AI Vendor": "",
                "BH Readiness": "",
                "Procurement Type": "",
                "Active Competitor": "",
                "Decision Makers": "",
                "Has Named Contact": "false",
                "Contact Name": "",
                "Contact Title": "",
                "Contact Email": "",
            }
        )

    # Sort: highest npi_count first (multi-site groups), then alpha by name.
    out_rows.sort(
        key=lambda r: (
            -int(r["Internal Notes"].split("npi_count=")[1].split(";")[0]),
            r["Organization Name"],
        )
    )

    write_csv(Path(args.out), out_rows)

    print(f"Wrote {len(out_rows)} rows to {args.out}")
    print(
        f"Stats: total_rows={stats['total_seen']:,}, "
        f"not_type2={stats['skipped_not_type2']:,}, "
        f"state_filtered={stats['skipped_state']:,}, "
        f"no_primary_care_taxonomy={stats['skipped_no_primary_care']:,}, "
        f"no_org_name={stats['skipped_no_org_name']:,}, "
        f"unique_orgs_pre_gate={len(org_data):,}, "
        f"size_gate_dropped={size_gate_dropped:,}, "
        f"noise_dropped={noise_dropped:,}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

