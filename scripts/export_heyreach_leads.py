#!/usr/bin/env python3
"""Export `wave1_linkedin_master.csv` to a HeyReach-ready flat file.

Output columns map directly to MCP / UI field names:
  profileUrl, firstName, lastName, companyName, position, persona,
  subtier, subtier_confidence, signal, source_query, notes,
  subtier_code, accept_priority

(`subtier_code` / `accept_priority` help you sort for fast iteration; strip before
HeyReach import if the tool rejects extra columns.)

Default filter (demo / feedback phase — tier mix across 1A–2C, tier 3 allowed):
  - persona is not "unknown" (you need a persona to pick a campaign)
  - persona_confidence in {high, medium}
  - signal_score >= min_signal (default 25, matches extractor threshold)

**Fast-iteration ranking:** Rows sort by `accept_priority` (higher = stronger proxy
for “likely fit” — not true LinkedIn activity; enrich externally if needed).

**Small batches:** `--per-subtier N` keeps the top N rows **per subtier code**
(1A…3C), each subtier sorted by `accept_priority`. Use 20–30 for early rounds.

Use --only-tier-1-2 to restrict to subtier codes 1A, 1B, 1C, 2A, 2B, 2C.

Usage:
  python3 scripts/export_heyreach_leads.py
  python3 scripts/export_heyreach_leads.py --per-subtier 30
  python3 scripts/export_heyreach_leads.py --only-tier-1-2 --min-signal 30 --per-subtier 25
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tam_builder.persona_rules import parse_subtier_code  # noqa: E402

TIER_1_2 = {"1A", "1B", "1C", "2A", "2B", "2C"}

# Stable ordering when emitting per-subtier batches
SUBTIER_BUCKET_ORDER = (
    "1A",
    "1B",
    "1C",
    "2A",
    "2B",
    "2C",
    "3A",
    "3B",
    "3C",
    "UNK",
)

DEFAULT_INPUT = REPO_ROOT / "fixtures" / "wave1_linkedin_master.csv"
DEFAULT_OUTPUT = REPO_ROOT / "fixtures" / "wave1_heyreach_ready.csv"

OUT_HEADERS = [
    "profileUrl",
    "firstName",
    "lastName",
    "companyName",
    "position",
    "persona",
    "subtier",
    "subtier_confidence",
    "signal",
    "source_query",
    "notes",
    "subtier_code",
    "accept_priority",
]


def split_full_name(raw: str) -> tuple[str, str]:
    """First token = firstName; remainder = lastName. Strip , MBA / , MD after comma."""
    s = (raw or "").strip().strip('"')
    if not s:
        return "", ""
    before_comma = s.split(",")[0].strip()
    parts = before_comma.split()
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def row_passes(
    row: dict[str, str],
    min_signal: int,
    only_tier_1_2: bool,
) -> bool:
    persona = (row.get("persona") or "").strip().lower()
    if persona == "unknown":
        return False
    conf = (row.get("persona_confidence") or "").strip().lower()
    if conf not in ("high", "medium"):
        return False
    try:
        sig = int(row.get("signal_score") or 0)
    except ValueError:
        sig = 0
    if sig < min_signal:
        return False

    code = parse_subtier_code(row.get("subtier_guess") or "")
    if only_tier_1_2 and code not in TIER_1_2:
        return False
    return True


def accept_priority(row: dict[str, str]) -> int:
    """Higher = better proxy for fast iteration (fit/clarity, not LinkedIn activity)."""
    try:
        sig = int(row.get("signal_score") or 0)
    except ValueError:
        sig = 0
    pc = (row.get("persona_confidence") or "").strip().lower()
    persona_pts = 3 if pc == "high" else (2 if pc == "medium" else 0)
    stc = (row.get("subtier_confidence") or "").strip().lower()
    subtier_pts = 2 if stc == "high" else (1 if stc == "medium" else 0)
    rationale = (row.get("persona_rationale") or "").strip().lower()
    keyword_pts = 5 if rationale.startswith("keyword:") else 0
    persona = (row.get("persona") or "").strip().lower()
    bh_pts = 12 if persona == "bh_quality_influencer" else 0
    return sig * 100 + persona_pts * 10 + subtier_pts + keyword_pts + bh_pts


def export_rows(
    input_path: Path,
    output_path: Path,
    min_signal: int,
    only_tier_1_2: bool,
    per_subtier_cap: int | None,
) -> tuple[int, int]:
    if not input_path.exists():
        raise FileNotFoundError(f"Missing master CSV: {input_path}")

    out_rows: list[dict[str, str]] = []
    total = 0
    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        expected = [
            "linkedin_profile_url",
            "persona",
            "persona_confidence",
            "persona_rationale",
            "signal_score",
            "subtier_guess",
            "subtier_confidence",
        ]
        missing = [c for c in expected if c not in fieldnames]
        if missing:
            raise ValueError(
                f"{input_path.name} must contain columns {expected}; missing: {missing}"
            )

        qualified: list[dict[str, str]] = []
        for row in reader:
            total += 1
            if not row_passes(row, min_signal, only_tier_1_2):
                continue
            qualified.append(row)

        if per_subtier_cap is not None and per_subtier_cap > 0:
            by_bucket: dict[str, list[dict[str, str]]] = defaultdict(list)
            for row in qualified:
                code = parse_subtier_code(row.get("subtier_guess") or "")
                key = code if code != "unknown" else "UNK"
                by_bucket[key].append(row)
            picked: list[dict[str, str]] = []
            seen: set[str] = set()
            for bucket in SUBTIER_BUCKET_ORDER:
                if bucket not in by_bucket:
                    continue
                chunk = sorted(
                    by_bucket[bucket],
                    key=lambda r: (-accept_priority(r), (r.get("linkedin_profile_url") or "")),
                )[:per_subtier_cap]
                picked.extend(chunk)
                seen.add(bucket)
            for bkey, rows in by_bucket.items():
                if bkey in seen:
                    continue
                chunk = sorted(
                    rows,
                    key=lambda r: (-accept_priority(r), (r.get("linkedin_profile_url") or "")),
                )[:per_subtier_cap]
                picked.extend(chunk)
            qualified = picked
        else:
            qualified = sorted(
                qualified,
                key=lambda r: (-accept_priority(r), (r.get("linkedin_profile_url") or "")),
            )

        for row in qualified:
            fn, ln = split_full_name(row.get("full_name") or "")
            code = parse_subtier_code(row.get("subtier_guess") or "")
            pri = accept_priority(row)
            out_rows.append(
                {
                    "profileUrl": (row.get("linkedin_profile_url") or "").strip(),
                    "firstName": fn,
                    "lastName": ln,
                    "companyName": (row.get("current_company") or "").strip(),
                    "position": (row.get("current_title") or "").strip(),
                    "persona": (row.get("persona") or "").strip(),
                    "subtier": (row.get("subtier_guess") or "").strip(),
                    "subtier_confidence": (row.get("subtier_confidence") or "").strip(),
                    "signal": str(row.get("signal_score") or "").strip(),
                    "source_query": (row.get("source_query") or "").strip(),
                    "notes": (row.get("notes") or "").strip(),
                    "subtier_code": code if code != "unknown" else "UNK",
                    "accept_priority": str(pri),
                }
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_HEADERS)
        w.writeheader()
        w.writerows(out_rows)

    return total, len(out_rows)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "-i",
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Source master CSV (default: {DEFAULT_INPUT.relative_to(REPO_ROOT)})",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output CSV (default: {DEFAULT_OUTPUT.relative_to(REPO_ROOT)})",
    )
    p.add_argument(
        "--min-signal",
        type=int,
        default=25,
        help="Minimum signal_score (default: 25)",
    )
    p.add_argument(
        "--only-tier-1-2",
        action="store_true",
        help="Keep only subtier 1A–2C (exclude 3A/3B/3C and unknown subtier)",
    )
    p.add_argument(
        "--per-subtier",
        type=int,
        default=None,
        metavar="N",
        help=(
            "Keep top N rows per subtier code (sorted by accept_priority). "
            "Typical early rounds: 20–30."
        ),
    )
    args = p.parse_args()

    try:
        total, kept = export_rows(
            args.input,
            args.output,
            args.min_signal,
            args.only_tier_1_2,
            args.per_subtier,
        )
    except (FileNotFoundError, ValueError) as e:
        sys.stderr.write(f"{e}\n")
        return 2

    sys.stdout.write(
        f"Read {total} rows from {args.input.relative_to(REPO_ROOT)} → "
        f"wrote {kept} rows to {args.output.relative_to(REPO_ROOT)}\n"
        f"  filter: persona≠unknown, confidence high|medium, signal>={args.min_signal}"
    )
    if args.only_tier_1_2:
        sys.stdout.write(", subtier in 1A–2C only")
    if args.per_subtier:
        sys.stdout.write(f", cap {args.per_subtier} per subtier (accept_priority sort)")
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
