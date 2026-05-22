from __future__ import annotations

import csv
import sys
from pathlib import Path

from tam_builder.josh_pilot.col4 import classify_col4
from tam_builder.josh_pilot.constants import (
    EXEC_CSV,
    FIXTURE_DIR,
    JOSH_ROW_FIELDS,
    NORMALIZED_EXTRA,
    PCP_CSV,
    READ_CSV,
)
from tam_builder.josh_pilot.read_buckets import parse_read_csv, write_read_yaml


def _row_to_dict(raw: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for i, key in enumerate(JOSH_ROW_FIELDS):
        out[key] = raw[i].strip() if i < len(raw) else ""
    return out


def normalize_josh_rows(
    path: Path,
    *,
    source: str,
) -> tuple[list[dict[str, str]], dict[str, int]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing Josh CSV: {path}")

    rows: list[dict[str, str]] = []
    stats = {"total": 0, "email_missing": 0, "col4_linkedin": 0, "col4_phone": 0}

    with path.open(newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        for raw in reader:
            if not raw or not any(cell.strip() for cell in raw):
                continue
            stats["total"] += 1
            row = _row_to_dict(raw)
            row["source"] = source
            email = row.get("email", "").strip()
            if not email:
                stats["email_missing"] += 1
                row["email_missing"] = "true"
            else:
                row["email_missing"] = "false"
            kind = classify_col4(row.get("col4_misc", ""))
            row["col4_kind"] = kind
            if kind == "linkedin":
                stats["col4_linkedin"] += 1
            elif kind == "phone":
                stats["col4_phone"] += 1
            rows.append(row)

    return rows, stats


def write_normalized_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(JOSH_ROW_FIELDS) + list(NORMALIZED_EXTRA)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def run_ingest(
    *,
    exec_path: Path = EXEC_CSV,
    pcp_path: Path = PCP_CSV,
    read_path: Path = READ_CSV,
    out_dir: Path = FIXTURE_DIR,
) -> dict[str, object]:
    out_dir.mkdir(parents=True, exist_ok=True)

    exec_rows, exec_stats = normalize_josh_rows(exec_path, source="josh_exec")
    pcp_rows, pcp_stats = normalize_josh_rows(pcp_path, source="josh_pcp_seed")

    write_normalized_csv(out_dir / "josh_exec_normalized.csv", exec_rows)
    write_normalized_csv(out_dir / "josh_pcp_seed.csv", pcp_rows)

    buckets = parse_read_csv(read_path)
    write_read_yaml(out_dir / "read_title_buckets.yaml", buckets)

    return {
        "exec_rows": len(exec_rows),
        "pcp_rows": len(pcp_rows),
        "exec_stats": exec_stats,
        "pcp_stats": pcp_stats,
    }


def main(argv: list[str] | None = None) -> int:
    try:
        summary = run_ingest()
    except FileNotFoundError as e:
        sys.stderr.write(f"{e}\n")
        return 2
    sys.stdout.write(
        f"Ingested exec={summary['exec_rows']} pcp={summary['pcp_rows']} → {FIXTURE_DIR}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
