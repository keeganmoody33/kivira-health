#!/usr/bin/env python3
"""JSONL → HeyReach CLI lead loader.

Reads Spider account-search JSONL checkpoint files (produced by
spider_account_search.py), applies the same precision filter (score_hit),
deduplicates by LinkedIn URL, and writes a flat JSON array in the schema
the heyreach-cli `lists add-leads` command expects.

Supported modes:
  2a   — 2A ACO accounts (named CMS contacts, high-precision name+org match)
  1c   — 1C provider group accounts (persona-title match, org match)
  1a   — 1A mid-market PCP groups (persona-title match, org match; same scoring as 1c)
  both — runs 2A then 1C, outputs two files

Output files:
  fixtures/heyreach_loads/heyreach_leads_2a.json
  fixtures/heyreach_loads/heyreach_leads_1c.json
  fixtures/heyreach_loads/heyreach_leads_1a.json

HeyReach lead schema (per heyreach-cli README):
  {
    "profileUrl":  "https://www.linkedin.com/in/...",
    "firstName":   "...",   # from contact_name (2A); empty for 1C
    "lastName":    "...",   # from contact_name (2A); empty for 1C
    "companyName": "...",   # from org
    "position":    ""       # blank — HeyReach enriches from profile
  }

Usage:
  # Process 2A JSONL:
  python3 scripts/build_heyreach_load.py --mode 2a \\
    --jsonl fixtures/wave1_runs/20260502T000500Z_smoke2/Q2A_progress.jsonl

  # Process 1C JSONL:
  python3 scripts/build_heyreach_load.py --mode 1c \\
    --jsonl fixtures/wave1_runs/20260502T013000Z_1c/Q1C_progress.jsonl

  # Both at once (auto-detects JSONL if omitted, or pass two paths):
  python3 scripts/build_heyreach_load.py --mode both \\
    --jsonl-2a fixtures/wave1_runs/20260502T000500Z_smoke2/Q2A_progress.jsonl \\
    --jsonl-1c fixtures/wave1_runs/20260502T013000Z_1c/Q1C_progress.jsonl

Precision filter defaults (same as spider_account_search.py smoke run):
  --min-id-matches 1   (at least 1 identity token must appear in URL+title+snippet)
  --min-org-matches 1  (at least 1 org token must appear)
  --top-n 1            (keep the single best-scoring hit per account)

  For 1C: identity tokens = PERSONA_TITLES_1C tokenized
          (no contact name available; title/snippet must mention a real title)

Shuffle (anti-bot pattern):
  --shuffle is ON by default with a fixed seed so output is deterministic but
  non-alphabetical. Override with --no-shuffle or --shuffle-seed <int>.

After running, load into HeyReach with:
  heyreach lists add-leads \\
    --list-id <YOUR_LIST_ID> \\
    --leads-json "$(cat fixtures/heyreach_loads/heyreach_leads_2a.json)"

  (Split into batches of ≤1000 if total exceeds that limit.)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.spider_account_search import (  # noqa: E402
    PERSONA_TITLES_1C,
    rank_and_take_top_n,
    tokenize,
)

LOADS_DIR = REPO_ROOT / "fixtures" / "heyreach_loads"

# Default JSONL paths (most recent run dirs as of 2026-05-02)
DEFAULT_2A_JSONL = (
    REPO_ROOT / "fixtures/wave1_runs/20260502T000500Z_smoke2/Q2A_progress.jsonl"
)
DEFAULT_1C_JSONL = (
    REPO_ROOT / "fixtures/wave1_runs/20260502T013000Z_1c/Q1C_progress.jsonl"
)


# ---------------------------------------------------------------------------
# Name splitting
# ---------------------------------------------------------------------------

def split_name(full_name: str) -> tuple[str, str]:
    """Split 'First Last' → ('First', 'Last').

    Handles:
    - 'First Last'          → ('First', 'Last')
    - 'First Middle Last'   → ('First', 'Middle Last')  [last word = surname]
    - 'Mononym'             → ('Mononym', '')
    - ''                    → ('', '')
    """
    parts = (full_name or "").strip().split()
    if not parts:
        return ("", "")
    if len(parts) == 1:
        return (parts[0], "")
    # First token → firstName; everything else → lastName (handles middle names)
    return (parts[0], " ".join(parts[1:]))


# ---------------------------------------------------------------------------
# Core processor
# ---------------------------------------------------------------------------

def process_jsonl(
    jsonl_path: Path,
    mode: str,
    min_id_matches: int,
    min_org_matches: int,
    top_n: int,
    shuffle: bool,
    shuffle_seed: int | None,
) -> list[dict]:
    """Read a JSONL file → apply precision filter → return HeyReach lead dicts.

    Args:
        jsonl_path:      Path to the Spider checkpoint JSONL.
        mode:            '2a' or '1c' — controls identity token source.
        min_id_matches:  Minimum identity-token matches required to keep a hit.
        min_org_matches: Minimum org-token matches required to keep a hit.
        top_n:           Best N hits to keep per account.
        shuffle:         Randomize order of records before processing.
        shuffle_seed:    Fixed seed for reproducible shuffle (None = random).

    Returns:
        List of HeyReach lead dicts (deduplicated by profileUrl).
    """
    if not jsonl_path.exists():
        sys.stderr.write(f"[ERROR] JSONL not found: {jsonl_path}\n")
        sys.exit(1)

    # Load all records
    records: list[dict] = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                sys.stderr.write(f"[WARN] Skipping malformed JSONL line: {exc}\n")

    if shuffle:
        import random as _random
        rng = _random.Random(shuffle_seed) if shuffle_seed is not None else _random.Random()
        rng.shuffle(records)

    # Build identity tokens for persona-based modes (1C and 1A share the same titles)
    shared_persona_identity_tokens: list[str] = []
    if mode in ("1c", "1a"):
        for title in PERSONA_TITLES_1C:
            shared_persona_identity_tokens.extend(tokenize(title))

    seen_urls: set[str] = set()
    leads: list[dict] = []
    skipped_zero_hits = 0
    skipped_score_fail = 0

    for obj in records:
        org_name = (obj.get("org") or "").strip()
        org_tokens = tokenize(org_name)
        raw_hits = obj.get("hits", [])

        if not raw_hits:
            skipped_zero_hits += 1
            continue

        # Identity tokens: named contact for 2A, persona titles for 1C/1A
        if mode == "2a":
            contact_name = (obj.get("contact_name") or "").strip()
            identity_tokens = tokenize(contact_name)
        else:
            identity_tokens = shared_persona_identity_tokens
            contact_name = ""

        ranked = rank_and_take_top_n(
            raw_hits,
            identity_tokens=identity_tokens,
            org_tokens=org_tokens,
            top_n=top_n,
            min_identity_matches=min_id_matches,
            min_org_matches=min_org_matches,
        )

        if not ranked:
            skipped_score_fail += 1
            continue

        for hit in ranked:
            url = (hit.get("linkedin_profile_url") or "").strip().rstrip("/")
            if not url:
                continue
            url_key = url.lower()
            if url_key in seen_urls:
                continue
            seen_urls.add(url_key)

            first, last = split_name(contact_name)
            leads.append(
                {
                    "profileUrl": url,
                    "firstName": first,
                    "lastName": last,
                    "companyName": org_name,
                    "position": "",          # HeyReach enriches from profile
                }
            )

    print(
        f"[{mode.upper()}] {len(records)} records → "
        f"{skipped_zero_hits} zero-hits skipped, "
        f"{skipped_score_fail} score-failed, "
        f"{len(leads)} leads kept (deduped by URL)"
    )
    return leads


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def write_leads(leads: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(leads, indent=2), encoding="utf-8")
    print(f"[OUT] {len(leads)} leads → {out_path}")


def print_runbook(out_path: Path, label: str) -> None:
    """Print the exact CLI commands to load this file into HeyReach."""
    print(f"\n── HeyReach CLI runbook ({label}) ──────────────────────────────")
    print("# 1. Create a list (one-time; reuse the ID for subsequent batches):")
    print(f'#    heyreach lists create --name "Wave 1 {label} — $(date +%Y-%m-%d)"')
    print()
    print("# 2. Add leads (replace LIST_ID with the ID from step 1):")
    print(f'#    heyreach lists add-leads \\')
    print(f'#      --list-id LIST_ID \\')
    print(f'#      --leads-json "$(cat {out_path})"')
    print()
    print("# 3. If the file exceeds 1000 leads, split and batch:")
    print(f'#    python3 -c "')
    print(f'#      import json, sys')
    print(f'#      leads = json.load(open(\\"{out_path}\\"))')
    print(f'#      for i, batch in enumerate([leads[j:j+1000] for j in range(0, len(leads), 1000)]):')
    print(f'#          open(f\\"{out_path.stem}_batch{{i}}.json\\", \\"w\\").write(json.dumps(batch))')
    print(f'#    "')
    print("# 4. Verify count in HeyReach UI or:")
    print("#    heyreach lists list")
    print("──────────────────────────────────────────────────────────────────\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(
        description="Build HeyReach-ready lead JSON from Spider JSONL checkpoint files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--mode",
        choices=["2a", "1c", "1a", "both"],
        required=True,
        help="Which JSONL(s) to process. 'both' runs 2a + 1c.",
    )
    p.add_argument(
        "--jsonl",
        help="JSONL path (use for --mode 2a, 1c, or 1a). Defaults to the most recent run dir.",
    )
    p.add_argument(
        "--jsonl-2a",
        help="2A JSONL path (used with --mode both). Defaults to most recent 2A run.",
    )
    p.add_argument(
        "--jsonl-1c",
        help="1C JSONL path (used with --mode both). Defaults to most recent 1C run.",
    )
    p.add_argument(
        "--out-dir",
        default=str(LOADS_DIR),
        help=f"Output directory for HeyReach JSON files. Default: {LOADS_DIR}",
    )
    p.add_argument(
        "--min-id-matches",
        type=int,
        default=1,
        help="Minimum identity-token matches to keep a hit (default: 1).",
    )
    p.add_argument(
        "--min-org-matches",
        type=int,
        default=1,
        help="Minimum org-token matches to keep a hit (default: 1).",
    )
    p.add_argument(
        "--top-n",
        type=int,
        default=1,
        help="Best N hits to keep per account (default: 1).",
    )
    p.add_argument(
        "--shuffle",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Shuffle record order before scoring (anti-bot; default: on).",
    )
    p.add_argument(
        "--shuffle-seed",
        type=int,
        default=42,
        help="Seed for shuffle (default: 42 for reproducibility).",
    )
    p.add_argument(
        "--runbook",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Print CLI runbook after writing output (default: on).",
    )
    args = p.parse_args()

    out_dir = Path(args.out_dir)

    common_kwargs = dict(
        min_id_matches=args.min_id_matches,
        min_org_matches=args.min_org_matches,
        top_n=args.top_n,
        shuffle=args.shuffle,
        shuffle_seed=args.shuffle_seed,
    )

    if args.mode in ("2a", "both"):
        jsonl_2a = Path(args.jsonl_2a or args.jsonl or DEFAULT_2A_JSONL)
        leads_2a = process_jsonl(jsonl_2a, mode="2a", **common_kwargs)
        out_2a = out_dir / "heyreach_leads_2a.json"
        write_leads(leads_2a, out_2a)
        if args.runbook:
            print_runbook(out_2a, "2A ACO")

    if args.mode in ("1c", "both"):
        jsonl_1c = Path(args.jsonl_1c or args.jsonl or DEFAULT_1C_JSONL)
        leads_1c = process_jsonl(jsonl_1c, mode="1c", **common_kwargs)
        out_1c = out_dir / "heyreach_leads_1c.json"
        write_leads(leads_1c, out_1c)
        if args.runbook:
            print_runbook(out_1c, "1C Provider Groups")

    if args.mode == "1a":
        jsonl_1a = Path(args.jsonl or DEFAULT_1C_JSONL)  # user must pass --jsonl for 1A
        leads_1a = process_jsonl(jsonl_1a, mode="1a", **common_kwargs)
        out_1a = out_dir / "heyreach_leads_1a.json"
        write_leads(leads_1a, out_1a)
        if args.runbook:
            print_runbook(out_1a, "1A Mid-Market PCP Groups")

    return 0


if __name__ == "__main__":
    sys.exit(main())
