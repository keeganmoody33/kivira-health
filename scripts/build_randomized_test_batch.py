#!/usr/bin/env python3
"""Build a randomized N-per-subtier test batch CSV for HeyReach.

Reads `fixtures/wave1_linkedin_master.csv`, parses subtier + intended role
from each row's `source_query` (e.g., Q1B-OO → subtier=1B, role=OO), samples
N leads per subtier (default 30), shuffles the combined list, and writes a
HeyReach-loadable CSV with persona+subtier labels per lead.

The randomization is intentional — it removes prioritization bias for a clean
A/B-style test where every subtier × role combo gets roughly equal treatment.

Usage:
  python3 scripts/build_randomized_test_batch.py
  python3 scripts/build_randomized_test_batch.py --per-subtier 30
  python3 scripts/build_randomized_test_batch.py --seed 42

Output: fixtures/randomized_test_batch.csv
"""

from __future__ import annotations

import argparse
import csv
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = REPO_ROOT / "fixtures" / "wave1_linkedin_master.csv"
DEFAULT_OUTPUT = REPO_ROOT / "fixtures" / "randomized_test_batch.csv"

# All canonical subtiers we care about for the test
CANONICAL_SUBTIERS = ["1A", "1B", "1C", "2A", "2B", "2C", "3A", "3B", "3C"]

# Map role codes (from query suffix) to readable role names
ROLE_CODE_TO_NAME = {
    "OO": "operational_owner",
    "CC": "clinical_champion",
    "EB": "economic_buyer",
    "TG": "tech_gatekeeper",
    "BH": "bh_quality_influencer",
    # 2B vendor-channel roles
    "PCL": "partnership_channel_lead",
    "PCO": "product_clinical_owner",
}

# Output schema for HeyReach loader compatibility
OUT_HEADERS = [
    "profileUrl",
    "firstName",
    "lastName",
    "companyName",
    "position",
    "subtier",
    "intended_role",
    "derived_persona",
    "signal_score",
    "source_query",
]


_QUERY_ID_RE = re.compile(r"^Q(\d[A-Z])(?:-([A-Z]+))?$")


def parse_subtier_role(source_query: str) -> tuple[str, str]:
    """Parse a source_query like 'Q1B-OO' → ('1B', 'OO').

    Returns ('', '') if unparseable. 'Q1A' (no suffix, from cached per-row run)
    returns ('1A', '') — subtier known, role unknown.
    """
    if not source_query:
        return "", ""
    m = _QUERY_ID_RE.match(source_query.strip())
    if not m:
        return "", ""
    return m.group(1), (m.group(2) or "")


def split_full_name(full: str) -> tuple[str, str]:
    parts = (full or "").strip().split(None, 1)
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--in", dest="input_csv", default=str(DEFAULT_INPUT))
    p.add_argument("--out", dest="output_csv", default=str(DEFAULT_OUTPUT))
    p.add_argument(
        "--per-subtier",
        type=int,
        default=30,
        help="How many leads to sample per subtier. Default 30.",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility. None = nondeterministic.",
    )
    args = p.parse_args(argv)

    rng = random.Random(args.seed)

    in_path = Path(args.input_csv)
    if not in_path.exists():
        print(f"ERROR: input not found: {in_path}", file=sys.stderr)
        return 2

    with in_path.open("r", encoding="utf-8-sig", newline="") as f:
        master_rows = list(csv.DictReader(f))
    print(f"Read {len(master_rows):,} rows from {in_path.relative_to(REPO_ROOT)}", file=sys.stderr)

    # Bucket by subtier
    by_subtier: dict[str, list[dict]] = defaultdict(list)
    skipped_no_subtier = 0
    skipped_no_url = 0
    for r in master_rows:
        url = (r.get("linkedin_profile_url") or "").strip()
        if not url:
            skipped_no_url += 1
            continue
        subtier, role = parse_subtier_role(r.get("source_query") or "")
        if subtier not in CANONICAL_SUBTIERS:
            skipped_no_subtier += 1
            continue
        by_subtier[subtier].append({**r, "_subtier": subtier, "_role": role})

    print(f"Bucketed into subtiers (skipped: no_url={skipped_no_url}, no_subtier={skipped_no_subtier}):", file=sys.stderr)
    for s in CANONICAL_SUBTIERS:
        print(f"  {s}: {len(by_subtier[s])}", file=sys.stderr)

    # Sample per subtier
    sampled: list[dict] = []
    for s in CANONICAL_SUBTIERS:
        pool = by_subtier[s]
        if not pool:
            print(f"  WARNING: subtier {s} has 0 leads — skipping", file=sys.stderr)
            continue
        n = min(args.per_subtier, len(pool))
        chosen = rng.sample(pool, n) if n < len(pool) else list(pool)
        sampled.extend(chosen)
        print(f"  Sampled {n}/{len(pool)} from {s}", file=sys.stderr)

    # Shuffle the combined list — kills any subtier ordering bias
    rng.shuffle(sampled)

    # Build output rows
    out_rows: list[dict[str, str]] = []
    for r in sampled:
        first, last = split_full_name(r.get("full_name") or "")
        intended_role_code = r["_role"]
        intended_role = ROLE_CODE_TO_NAME.get(intended_role_code, intended_role_code or "unknown")
        out_rows.append(
            {
                "profileUrl": r["linkedin_profile_url"],
                "firstName": first,
                "lastName": last,
                "companyName": r.get("current_company") or "",
                "position": r.get("current_title") or "",
                "subtier": r["_subtier"],
                "intended_role": intended_role,
                "derived_persona": r.get("persona") or "",
                "signal_score": r.get("signal_score") or "0",
                "source_query": r.get("source_query") or "",
            }
        )

    out_path = Path(args.output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_HEADERS)
        writer.writeheader()
        for r in out_rows:
            writer.writerow(r)

    print(f"\nWrote {len(out_rows)} randomized leads to {out_path.relative_to(REPO_ROOT)}", file=sys.stderr)
    print(f"Subtier distribution in output:", file=sys.stderr)
    from collections import Counter
    sub_counts = Counter(r["subtier"] for r in out_rows)
    for s in CANONICAL_SUBTIERS:
        if s in sub_counts:
            print(f"  {s}: {sub_counts[s]}", file=sys.stderr)
    role_counts = Counter(r["intended_role"] for r in out_rows)
    print(f"\nIntended role distribution:", file=sys.stderr)
    for role, c in sorted(role_counts.items(), key=lambda x: -x[1]):
        print(f"  {role}: {c}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
