#!/usr/bin/env python3
"""Clay round-trip helpers for the Kivira TAM builder.

This script does NOT call Clay's API. It creates and consumes CSVs so Clay can be used as a UI-driven
waterfall enrichment layer.

Two modes:

1) export: take a normalized CSV and emit a Clay-import-friendly CSV (stable column names)
2) import: take a Clay-exported CSV and map it back into TAM-builder-friendly headers
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

# Ensure repo-local imports work when running as a script.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tam_builder.constants import NORMALIZED_ACCOUNT_FIELDS
from tam_builder.normalize import normalize_accounts


CLAY_EXPORT_FIELD_MAP = {
    # Clay output columns vary by workflow. Add mappings here as you standardize the Clay table.
    # Keys are expected Clay column titles, values are TAM canonical field names.
    "Organization Name": "org_name",
    "State": "state",
    "City": "city",
    "Organization Type": "org_type",
    "Priority Personas": "priority_personas",
    "Candidate Ceiling": "max_candidates",
    "Notes": "notes",
    "Parent Org": "parent_org_name",
    "System Affiliation": "system_affiliation",
    "Value-Based Track": "vbc_track",
    "Primary EHR": "ehr",
    "Payer Mix": "payer_mix",
    "Ambient AI Vendor": "ambient_ai",
    "BH Readiness": "bh_readiness",
    "Procurement Type": "procurement_type",
    "Active Competitor": "active_competitor",
    "Decision Makers": "decision_maker_count",
    "Has Named Contact": "identified_contact",
    "Contact Name": "contact_name",
    "Contact Title": "contact_title",
    "Contact Email": "contact_email",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [dict((k or "").strip(), (v or "").strip()) for k, v in reader]


def write_csv(path: Path, rows: list[dict[str, str]], headers: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({h: row.get(h, "") for h in headers})


def export_for_clay(normalized_csv: Path, out_csv: Path) -> None:
    rows = read_csv(normalized_csv)
    # Ensure already-normalized CSVs still match the schema; this is a lightweight validation pass.
    normalized_rows, errors, _ = normalize_accounts(rows)
    if errors:
        errors_path = out_csv.with_suffix(".errors.csv")
        write_csv(errors_path, errors, ["row_number", "field", "value", "message"])
        raise SystemExit(f"Input has normalization errors. See {errors_path}")

    clay_headers = [
        "Organization Name",
        "State",
        "City",
        "Organization Type",
        "Priority Personas",
        "Candidate Ceiling",
        "Notes",
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

    clay_rows: list[dict[str, str]] = []
    for r in normalized_rows:
        clay_rows.append(
            {
                "Organization Name": str(r.get("org_name", "")),
                "State": str(r.get("state", "")),
                "City": str(r.get("city", "")),
                "Organization Type": str(r.get("org_type", "")),
                "Priority Personas": str(r.get("priority_personas", "")),
                "Candidate Ceiling": str(r.get("max_candidates", "")),
                "Notes": str(r.get("notes", "")),
                "Parent Org": str(r.get("parent_org_name", "")),
                "System Affiliation": str(r.get("system_affiliation", "")),
                "Value-Based Track": str(r.get("vbc_track", "")),
                "Primary EHR": str(r.get("ehr", "")),
                "Payer Mix": str(r.get("payer_mix", "")),
                "Ambient AI Vendor": str(r.get("ambient_ai", "")),
                "BH Readiness": str(r.get("bh_readiness", "")),
                "Procurement Type": str(r.get("procurement_type", "")),
                "Active Competitor": str(r.get("active_competitor", "")),
                "Decision Makers": str(r.get("decision_maker_count", "")),
                "Has Named Contact": str(r.get("identified_contact", "")),
                "Contact Name": str(r.get("contact_name", "")),
                "Contact Title": str(r.get("contact_title", "")),
                "Contact Email": str(r.get("contact_email", "")),
            }
        )

    write_csv(out_csv, clay_rows, clay_headers)


def import_from_clay(clay_export_csv: Path, out_csv: Path) -> None:
    rows = read_csv(clay_export_csv)
    mapped: list[dict[str, str]] = []
    for row in rows:
        out: dict[str, str] = {}
        for clay_col, canonical in CLAY_EXPORT_FIELD_MAP.items():
            if clay_col in row and row[clay_col] != "":
                out[canonical] = row[clay_col]
        mapped.append(out)

    # Normalize back into the full schema using existing aliases and validation.
    normalized_rows, errors, _ = normalize_accounts(mapped)
    write_csv(out_csv, [{k: str(r.get(k, "")) for k in NORMALIZED_ACCOUNT_FIELDS} for r in normalized_rows], NORMALIZED_ACCOUNT_FIELDS)
    if errors:
        errors_path = out_csv.with_suffix(".errors.csv")
        write_csv(errors_path, errors, ["row_number", "field", "value", "message"])


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Clay CSV round-trip for Kivira TAM builder.")
    sub = p.add_subparsers(dest="cmd", required=True)

    exp = sub.add_parser("export", help="Export a normalized CSV to Clay-friendly headers.")
    exp.add_argument("--input", required=True)
    exp.add_argument("--output", required=True)

    imp = sub.add_parser("import", help="Import a Clay-exported CSV and normalize into TAM schema.")
    imp.add_argument("--input", required=True)
    imp.add_argument("--output", required=True)

    args = p.parse_args(argv)
    if args.cmd == "export":
        export_for_clay(Path(args.input), Path(args.output))
    else:
        import_from_clay(Path(args.input), Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

