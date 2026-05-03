#!/usr/bin/env python3
"""Build Wave 2 raw account lists for Tier 2B (Clinical Champion) and Tier 2C
(Economic Buyer / Contract) by pivoting different persona columns out of the
CMS MSSP PY2026 CSV.

The MSSP CSV is the same one used by `build_list_1c_2a.py` (which extracts the
2A operational-owner contact via `ACO_Exec_Name`). This script extracts:

  - 2B (Clinical Champion):  `ACO_Medical_Director_Name`
  - 2C (Economic Buyer):     `ACO_Compliance_Contact_Name`

Dedup is at the ACO_ID level — one named contact per ACO per persona.

Inputs:
- CMS MSSP PY2026 CSV (e.g. `artifacts/mssp_py2026.csv`)

Outputs (default):
- `fixtures/wave2_2b_raw_accounts.csv`  (clinical-quality lead per ACO)
- `fixtures/wave2_2c_raw_accounts.csv`  (compliance/contract lead per ACO)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from pathlib import Path


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


PERSONA_SPEC = {
    # subtier -> (name_column, default_contact_title, persona_label)
    "2B": (
        "ACO_Medical_Director_Name",
        "ACO Medical Director (per CMS public filing)",
        "clinical_champion",
    ),
    "2C": (
        "ACO_Compliance_Contact_Name",
        "ACO Compliance Contact (per CMS public filing)",
        "economic_buyer",
    ),
}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader]


def _stable_source_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:10]
    return f"{prefix}-{h}"


def _first_state(value: str) -> str:
    """ACO_Service_Area can be a comma-separated state list. Take the first."""
    v = (value or "").strip()
    if "," in v:
        v = v.split(",", 1)[0].strip()
    return v.upper()


def parse_mssp_for_persona(
    rows: list[dict[str, str]],
    subtier: str,
) -> list[dict[str, str]]:
    """Pivot MSSP rows on the persona-specific name column.

    Dedup at ACO_ID level. Returns RAW_HEADERS-shaped row dicts.
    """
    if subtier not in PERSONA_SPEC:
        raise ValueError(f"Unknown subtier {subtier}; expected one of {list(PERSONA_SPEC)}")

    name_col, default_title, persona_label = PERSONA_SPEC[subtier]

    seen_aco_ids: set[str] = set()
    out: list[dict[str, str]] = []

    for row in rows:
        aco_id = (row.get("ACO_ID") or "").strip()
        aco_name = (row.get("ACO_Name") or "").strip()
        contact_name = (row.get(name_col) or "").strip()

        if not aco_id or not aco_name or not contact_name:
            continue
        if aco_id in seen_aco_ids:
            continue
        seen_aco_ids.add(aco_id)

        state = _first_state(row.get("ACO_Service_Area") or "")

        out.append(
            {
                "Organization Name": aco_name,
                "State Code": state,
                "Metro": "",
                "Organization Type": "aco_parent",
                "Priority Personas": persona_label,
                "Candidate Ceiling": "1",  # one named contact per ACO
                "Internal Notes": f"wave=2; subtier={subtier}; source=CMS_MSSP_PY2026; persona={persona_label}",
                "Source System": "Public",
                "Source ID": _stable_source_id(f"MSSP-{subtier}", aco_id, persona_label),
                "Parent Org": "",
                "System Affiliation": "",
                "Value-Based Track": "MSSP ACO",
                "Primary EHR": "",
                "Payer Mix": "",
                "Ambient AI Vendor": "",
                "BH Readiness": "",
                "Procurement Type": "",
                "Active Competitor": "",
                "Decision Makers": "",
                "Has Named Contact": "true",
                "Contact Name": contact_name,
                "Contact Title": default_title,
                "Contact Email": "",
            }
        )

    return out


def write_raw_accounts(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_HEADERS)
        writer.writeheader()
        for r in rows:
            writer.writerow({h: r.get(h, "") for h in RAW_HEADERS})


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Pivot CMS MSSP CSV into 2B/2C named-contact raw accounts."
    )
    p.add_argument(
        "--mssp-csv",
        required=True,
        help="Path to CMS MSSP PY2026 participant CSV.",
    )
    p.add_argument(
        "--out-2b",
        default=str(Path("fixtures") / "wave2_2b_raw_accounts.csv"),
        help="Output CSV for 2B (clinical-quality / medical-director persona).",
    )
    p.add_argument(
        "--out-2c",
        default=str(Path("fixtures") / "wave2_2c_raw_accounts.csv"),
        help="Output CSV for 2C (compliance/contract persona).",
    )
    args = p.parse_args(argv)

    mssp_path = Path(args.mssp_csv)
    if not mssp_path.exists():
        print(f"MSSP CSV not found: {mssp_path}", file=sys.stderr)
        return 2

    rows = read_csv_rows(mssp_path)
    print(f"Loaded {len(rows):,} MSSP rows from {mssp_path}", file=sys.stderr)

    rows_2b = parse_mssp_for_persona(rows, "2B")
    rows_2c = parse_mssp_for_persona(rows, "2C")

    write_raw_accounts(Path(args.out_2b), rows_2b)
    write_raw_accounts(Path(args.out_2c), rows_2c)

    print(f"Wrote {len(rows_2b)} 2B (clinical-champion) accounts to {args.out_2b}")
    print(f"Wrote {len(rows_2c)} 2C (economic-buyer) accounts to {args.out_2c}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
