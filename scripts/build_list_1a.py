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
import sys
from collections import defaultdict
from pathlib import Path


PRIMARY_CARE_TAXONOMY_CODES = {
    "207Q00000X",  # Family Medicine
    "207R00000X",  # Internal Medicine
    "207QA0505X",  # Adult Medicine
    "363L00000X",  # Nurse Practitioner (Primary Care)
}


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


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Build Wave 2 list (1A mid-market groups).")
    p.add_argument("--nppes-csv", required=True, help="Path to NPPES CSV (full or subset).")
    p.add_argument("--cms-doctors-csv", help="Optional: CMS Doctors & Clinicians export CSV.")
    p.add_argument("--out", default=str(Path("fixtures") / "wave2_raw_accounts.csv"))
    p.add_argument("--states", help="Optional comma-separated list of 2-letter states to include.")
    p.add_argument("--min-pcps", type=int, default=10, help="Lower bound for PCP count filter.")
    p.add_argument("--max-pcps", type=int, default=30, help="Upper bound for PCP count filter.")
    p.add_argument("--candidate-ceiling", type=int, default=150)
    args = p.parse_args(argv)

    nppes_path = Path(args.nppes_csv)
    state_filter = None
    if args.states:
        state_filter = {s.strip().upper() for s in args.states.split(",") if s.strip()}

    pcp_counts: dict[str, int] = {}
    if args.cms_doctors_csv:
        cms_rows = read_csv(Path(args.cms_doctors_csv))
        pcp_counts = build_pcp_counts_from_cms_doctors(cms_rows)

    out_rows: list[dict[str, str]] = []
    skipped_no_primary_care = 0
    skipped_state = 0
    skipped_not_type2 = 0
    skipped_pcp_range = 0

    # Use streaming reader for the NPPES file — it can exceed 10GB and will OOM
    # if loaded all at once via read_csv(). stream_csv() yields one row at a time.
    nppes_rows = stream_csv(nppes_path)

    total_seen = 0
    for row in nppes_rows:
        total_seen += 1
        if total_seen % 500_000 == 0:
            print(f"  {total_seen:,} rows scanned — {len(out_rows):,} kept so far...", file=sys.stderr, flush=True)

        if not nppes_is_type2_org(row):
            skipped_not_type2 += 1
            continue

        st = nppes_state(row).upper()
        if state_filter and st not in state_filter:
            skipped_state += 1
            continue

        org_name = nppes_org_name(row)
        if not org_name:
            continue

        if not (nppes_taxonomy_codes(row) & PRIMARY_CARE_TAXONOMY_CODES):
            skipped_no_primary_care += 1
            continue

        # If we have PCP counts, enforce mid-market window; otherwise keep row and mark for later sizing.
        pcp_count = None
        if pcp_counts:
            # We don't have a deterministic join key without additional prep; best-effort join by org name.
            pcp_count = pcp_counts.get(org_name)
            if pcp_count is not None and not (args.min_pcps <= pcp_count <= args.max_pcps):
                skipped_pcp_range += 1
                continue

        notes = "wave=2; subtier=1A; source=NPPES"
        if pcp_count is None:
            notes += "; pcp_count=unknown"
        else:
            notes += f"; pcp_count={pcp_count}"

        out_rows.append(
            {
                "Organization Name": org_name,
                "State Code": st,
                "Metro": "",
                "Organization Type": "independent_group",
                "Priority Personas": "",
                "Candidate Ceiling": str(args.candidate_ceiling),
                "Internal Notes": notes,
                "Source System": "Public",
                "Source ID": "",
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

    write_csv(Path(args.out), out_rows)

    print(f"Wrote {len(out_rows)} rows to {args.out}")
    print(
        "Skipped:",
        f"not_type2={skipped_not_type2}, state_filtered={skipped_state}, "
        f"no_primary_care_taxonomy={skipped_no_primary_care}, pcp_out_of_range={skipped_pcp_range}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

