from __future__ import annotations

import csv
import sys
from pathlib import Path

from tam_builder.josh_pilot.col4 import normalize_linkedin_url
from tam_builder.josh_pilot.constants import (
    FIXTURE_DIR,
    PERSONA_PRIORITY,
)
from tam_builder.josh_pilot.read_buckets import is_non_pcp_org
from tam_builder.persona_rules import tag_persona_keyword

ALLOWED_ORG_TYPES = (
    "single/multi-specialty physician group",
    "independent practice association",
)

METRIC_MIN = 3
METRIC_MAX = 50


def _metric_ok(raw: str) -> bool:
    try:
        v = int((raw or "").strip())
    except ValueError:
        return False
    return METRIC_MIN <= v <= METRIC_MAX


def _org_allowed(org_type: str) -> bool:
    ot = (org_type or "").lower().strip()
    return any(a in ot for a in ALLOWED_ORG_TYPES)


def _persona_rank(persona: str) -> int:
    try:
        return PERSONA_PRIORITY.index(persona)
    except ValueError:
        return 99


def filter_row(row: dict[str, str]) -> tuple[bool, str]:
    if row.get("source") == "josh_pcp_seed":
        return True, "pcp_seed_force"

    if not _org_allowed(row.get("org_type", "")):
        return False, "org_type_excluded"

    if not _metric_ok(row.get("size_metric", "")):
        return False, "size_metric_out_of_band"

    if is_non_pcp_org(row.get("org_name", ""), row.get("title_raw", "")):
        return False, "non_pcp_org_blocklist"

    tag = tag_persona_keyword(row.get("title_raw", ""), row.get("org_name", ""))
    if tag["persona"] == "unknown" and tag["confidence"] == "high":
        return False, f"disqualified:{tag['rationale']}"
    if tag["persona"] == "unknown":
        return False, "persona_unknown"

    return True, "ok"


def dedupe_by_org(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    best: dict[str, dict[str, str]] = {}
    for row in rows:
        org = (row.get("org_name") or "").strip().lower()
        if not org:
            continue
        tag = tag_persona_keyword(row.get("title_raw", ""), row.get("org_name", ""))
        row = dict(row)
        row["persona"] = tag["persona"]
        row["persona_confidence"] = tag["confidence"]
        row["persona_rationale"] = tag["rationale"]
        url = normalize_linkedin_url(row.get("col4_misc", ""))
        if url:
            row["linkedin_profile_url_hint"] = url

        prev = best.get(org)
        if not prev or _persona_rank(tag["persona"]) < _persona_rank(
            prev.get("persona", "unknown")
        ):
            best[org] = row
    return list(best.values())


def run_filter(
    *,
    exec_csv: Path = FIXTURE_DIR / "josh_exec_normalized.csv",
    pcp_csv: Path = FIXTURE_DIR / "josh_pcp_seed.csv",
    out_csv: Path = FIXTURE_DIR / "candidates_filtered.csv",
) -> dict[str, int]:
    rows: list[dict[str, str]] = []
    stats = {"input": 0, "kept": 0, "dropped": 0}

    for path in (exec_csv, pcp_csv):
        if not path.exists():
            raise FileNotFoundError(path)
        with path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stats["input"] += 1
                ok, reason = filter_row(row)
                if not ok:
                    stats["dropped"] += 1
                    continue
                row = dict(row)
                row["filter_reason"] = reason
                rows.append(row)

    deduped = dedupe_by_org(rows)
    stats["kept"] = len(deduped)

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    if deduped:
        fields = list(deduped[0].keys())
        with out_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(deduped)

    return stats


def main() -> int:
    try:
        stats = run_filter()
    except FileNotFoundError as e:
        sys.stderr.write(f"{e}\n")
        return 2
    sys.stdout.write(
        f"Filter: in={stats['input']} kept={stats['kept']} dropped={stats['dropped']}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
