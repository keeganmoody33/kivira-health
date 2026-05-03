#!/usr/bin/env python3
"""Snippet-only persona/subtier extractor — bypass Parallel.ai for cached Spider runs.

Spider's /search endpoint returns `title` snippets that already contain
"<Person Name> - <Role Title> at <Company> | LinkedIn"-shaped strings. That's
enough to run `tag_persona_keyword()` and `refine_subtier_1a()` from
`tam_builder.persona_rules` directly, without hitting Parallel.ai's per-URL
profile-scrape cost.

Use this for the bulk of cached results. Only fall back to the Parallel path
for rows where the snippet is truncated or persona = unknown after keyword tagging.

Inputs:
  fixtures/wave1_runs/<timestamp>/Q*_raw_urls.json

Outputs (appended, deduped on linkedin_profile_url):
  fixtures/wave1_linkedin_master.csv

Usage:
  python3 scripts/extract_from_search_snippets.py --latest
  python3 scripts/extract_from_search_snippets.py --run 20260502T110336Z
  python3 scripts/extract_from_search_snippets.py --latest --account-1a-csv fixtures/wave2_1a_raw_accounts.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tam_builder.persona_rules import (  # noqa: E402
    refine_subtier_1a,
    tag_persona_keyword,
)

RUNS_DIR = REPO_ROOT / "fixtures" / "wave1_runs"
MASTER_CSV = REPO_ROOT / "fixtures" / "wave1_linkedin_master.csv"

CSV_HEADERS = [
    "linkedin_profile_url",
    "full_name",
    "current_title",
    "current_company",
    "persona",
    "persona_confidence",
    "persona_rationale",
    "subtier_guess",
    "subtier_confidence",
    "signal_score",
    "location",
    "source_query",
    "date_captured",
    "heyreach_campaign",
    "notes",
]


# ---------------------------------------------------------------------------
# Snippet parsing
# ---------------------------------------------------------------------------

# Trailing "| LinkedIn" or "| Link..." (may be truncated).
_LINKEDIN_SUFFIX_RE = re.compile(r"\s*\|\s*Link[a-zA-Z]*\.?\s*$")
# "<title> at <company>" — the most common LinkedIn snippet shape.
_AT_SPLIT_RE = re.compile(r"\s+at\s+", re.IGNORECASE)


def parse_snippet(title: str) -> dict[str, str]:
    """Parse a Spider search-result `title` into {full_name, role_title, company}.

    Common shapes:
      "Jane Doe - VP Operations at Acme Medical Group | LinkedIn"
      "Jane Doe, MBA - VP Operations - Acme Medical Group | LinkedIn"
      "Jane Doe - Practice Manager"
    """
    if not title:
        return {"full_name": "", "role_title": "", "company": ""}

    s = _LINKEDIN_SUFFIX_RE.sub("", title).strip()

    # Split into segments on " - "
    parts = [p.strip() for p in s.split(" - ") if p.strip()]
    if not parts:
        return {"full_name": "", "role_title": "", "company": ""}

    full_name = parts[0]
    role_title = ""
    company = ""

    if len(parts) >= 3:
        role_title = parts[1]
        company = " - ".join(parts[2:])
    elif len(parts) == 2:
        rest = parts[1]
        # "Title at Company" pattern
        at_match = _AT_SPLIT_RE.split(rest, maxsplit=1)
        if len(at_match) == 2:
            role_title, company = at_match[0].strip(), at_match[1].strip()
        else:
            role_title = rest

    # Strip credentials/suffixes from name (anything after a comma)
    full_name = full_name.split(",")[0].strip()
    # Strip company trailing " | Link..." artefacts that survived
    company = _LINKEDIN_SUFFIX_RE.sub("", company).strip()
    return {
        "full_name": full_name,
        "role_title": role_title,
        "company": company,
    }


# ---------------------------------------------------------------------------
# Signal scoring
# ---------------------------------------------------------------------------


def compute_signal_score(
    persona_conf: str,
    persona: str,
    subtier_conf: str,
    company_in_1a_list: bool,
) -> int:
    """Heuristic signal_score 0-50.

    Mirrors the philosophy of the Parallel-extractor's score: persona-confidence
    is the primary driver, with bumps for subtier match and 1A list overlap.
    """
    base = {"high": 30, "medium": 20, "low": 10}.get(persona_conf, 0)
    if persona == "unknown":
        return 0
    if persona == "bh_quality_influencer":
        base += 5  # BH influencer is strategically valuable for Kivira
    if subtier_conf == "high":
        base += 5
    if company_in_1a_list:
        base += 10
    return min(base, 50)


# ---------------------------------------------------------------------------
# Account-list back-tagging
# ---------------------------------------------------------------------------


def load_1a_account_names(csv_path: Path | None) -> set[str]:
    """Lower-cased set of 1A org names, used as back-tag verifier."""
    if not csv_path or not csv_path.exists():
        return set()
    out: set[str] = set()
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("Organization Name") or "").strip()
            if name:
                out.add(name.lower())
    return out


def company_matches_1a(company: str, account_names: set[str]) -> bool:
    """Loose match: any 1A account name appears as a substring of company (or vice versa)."""
    if not company or not account_names:
        return False
    c = company.lower().strip()
    if c in account_names:
        return True
    # Loose substring match — handles common suffixes like ", LLC" / "Inc"
    for n in account_names:
        if len(n) > 8 and (n in c or c in n):
            return True
    return False


# ---------------------------------------------------------------------------
# Run discovery + master CSV management
# ---------------------------------------------------------------------------


def latest_run_dir() -> Path | None:
    if not RUNS_DIR.exists():
        return None
    runs = sorted(p for p in RUNS_DIR.iterdir() if p.is_dir() and not p.name.startswith(("TEST_", "_")))
    return runs[-1] if runs else None


def collect_results(run_dir: Path) -> Iterable[dict]:
    for f in sorted(run_dir.glob("Q*_raw_urls.json")):
        payload = json.loads(f.read_text(encoding="utf-8"))
        for r in payload.get("results", []):
            yield {
                "linkedin_profile_url": (r.get("linkedin_profile_url") or "").strip(),
                "title_snippet": r.get("title", ""),
                "snippet_text": r.get("snippet", ""),
                "source_query": payload.get("query_id", ""),
                "expected_subtiers": payload.get("expected_subtiers", []),
            }


def load_existing_urls(path: Path) -> set[str]:
    if not path.exists():
        return set()
    out: set[str] = set()
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = (row.get("linkedin_profile_url") or "").strip().lower().rstrip("/")
            if url:
                out.add(url)
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--latest", action="store_true")
    g.add_argument("--run", help="Run directory timestamp")
    p.add_argument(
        "--account-1a-csv",
        default=str(REPO_ROOT / "fixtures" / "wave2_1a_raw_accounts.csv"),
        help="Optional 1A account list for back-tag confidence boost.",
    )
    p.add_argument(
        "--master-csv",
        default=str(MASTER_CSV),
        help="Master CSV to append into.",
    )
    args = p.parse_args(argv)

    if args.latest:
        run_dir = latest_run_dir()
        if not run_dir:
            print("No run directories found.", file=sys.stderr)
            return 2
    else:
        run_dir = RUNS_DIR / args.run
        if not run_dir.exists():
            print(f"Run dir not found: {run_dir}", file=sys.stderr)
            return 2

    print(f"[snippet-extract] reading {run_dir.relative_to(REPO_ROOT)}", file=sys.stderr)

    account_names = load_1a_account_names(Path(args.account_1a_csv))
    if account_names:
        print(f"[snippet-extract] loaded {len(account_names):,} 1A account names for back-tag", file=sys.stderr)

    master_path = Path(args.master_csv)
    existing_urls = load_existing_urls(master_path)
    if existing_urls:
        print(f"[snippet-extract] master has {len(existing_urls):,} existing URLs", file=sys.stderr)

    # Collect, dedupe, classify
    seen_urls: set[str] = set()
    new_rows: list[dict[str, str]] = []
    stats = {
        "total": 0,
        "duplicate_in_run": 0,
        "already_in_master": 0,
        "no_snippet": 0,
        "persona_unknown": 0,
        "kept": 0,
    }
    persona_counts: dict[str, int] = {}

    for r in collect_results(run_dir):
        stats["total"] += 1
        url = r["linkedin_profile_url"].strip()
        norm = url.lower().rstrip("/")
        if not url:
            continue
        if norm in seen_urls:
            stats["duplicate_in_run"] += 1
            continue
        seen_urls.add(norm)
        if norm in existing_urls:
            stats["already_in_master"] += 1
            continue

        parsed = parse_snippet(r["title_snippet"])
        full_name = parsed["full_name"]
        role_title = parsed["role_title"]
        company = parsed["company"]

        if not role_title:
            stats["no_snippet"] += 1
            continue

        tag = tag_persona_keyword(role_title, company)
        persona = tag["persona"]
        if persona == "unknown":
            stats["persona_unknown"] += 1
            # We still write unknowns with score=0 so dedup works on next run.
            # export_heyreach_leads.py filters them out by persona.

        # Subtier: heuristic from company alone via refine_subtier_1a (with no
        # prior guess, it returns the best-effort 1A vs other)
        subtier_guess, subtier_conf = refine_subtier_1a("1A", company)

        in_1a = company_matches_1a(company, account_names)
        score = compute_signal_score(
            persona_conf=tag["confidence"],
            persona=persona,
            subtier_conf=subtier_conf,
            company_in_1a_list=in_1a,
        )

        notes = ""
        if in_1a:
            notes = "company_in_1a_account_list"

        new_rows.append(
            {
                "linkedin_profile_url": url,
                "full_name": full_name,
                "current_title": role_title,
                "current_company": company,
                "persona": persona,
                "persona_confidence": tag["confidence"],
                "persona_rationale": tag["rationale"],
                "subtier_guess": subtier_guess,
                "subtier_confidence": subtier_conf,
                "signal_score": str(score),
                "location": "",
                "source_query": r["source_query"],
                "date_captured": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "heyreach_campaign": "",
                "notes": notes,
            }
        )
        persona_counts[persona] = persona_counts.get(persona, 0) + 1
        stats["kept"] += 1

    # Append to master
    master_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not master_path.exists() or master_path.stat().st_size == 0
    with master_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if write_header:
            writer.writeheader()
        for r in new_rows:
            writer.writerow({h: r.get(h, "") for h in CSV_HEADERS})

    print(f"[snippet-extract] wrote {stats['kept']:,} new rows to {master_path.relative_to(REPO_ROOT)}", file=sys.stderr)
    print(
        f"[snippet-extract] stats: total={stats['total']}, "
        f"duplicate_in_run={stats['duplicate_in_run']}, "
        f"already_in_master={stats['already_in_master']}, "
        f"no_snippet={stats['no_snippet']}, "
        f"persona_unknown={stats['persona_unknown']}",
        file=sys.stderr,
    )
    print("[snippet-extract] persona distribution (incl. unknown):", file=sys.stderr)
    for persona, count in sorted(persona_counts.items(), key=lambda x: -x[1]):
        print(f"  {persona}: {count}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
