#!/usr/bin/env python3
"""Spider.cloud query runner — Wave 1 LinkedIn URL sourcing.

Reads `fixtures/wave1_linkedin_queries.md`, runs each Boolean query through
Spider.cloud's /search endpoint with `site:linkedin.com/in` appended, filters
results to LinkedIn profile URLs only, dedupes against the master CSV, and
writes per-query JSON files into `fixtures/wave1_runs/<UTC-timestamp>/`.

Output JSON structure (per query):
    {
      "query_id": "Q1",
      "query_string": "(...) site:linkedin.com/in",
      "industry_filter": "Hospital & Health Care",
      "location": "United States",
      "expected_subtiers": ["1A", "1C", "3A", "3B"],
      "run_at": "2026-05-01T16:23:00Z",
      "raw_result_count": 47,
      "deduped_result_count": 47,
      "results": [
        {"linkedin_profile_url": "...", "title": "...", "snippet": "..."}
      ]
    }

Usage:
    python scripts/spider_query_runner.py --query Q1
    python scripts/spider_query_runner.py --all
    python scripts/spider_query_runner.py --query Q1 --dry-run

Required env vars (loaded from .env.local):
    SPIDER_API_KEY
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
QUERIES_FILE = REPO_ROOT / "fixtures" / "wave1_linkedin_queries.md"
MASTER_CSV = REPO_ROOT / "fixtures" / "wave1_linkedin_master.csv"
RUNS_DIR = REPO_ROOT / "fixtures" / "wave1_runs"
ENV_FILE = REPO_ROOT / ".env.local"

SPIDER_SEARCH_URL = "https://api.spider.cloud/search"
SPIDER_TIMEOUT_SECONDS = 60

# We always append this to the Boolean before sending to Spider — it's the
# Google X-ray operator that constrains results to LinkedIn person profiles.
LINKEDIN_PERSON_OPERATOR = "site:linkedin.com/in"

# Regex that matches a LinkedIn person profile URL. Company pages live at
# /company/, school at /school/, etc. — we only want /in/.
LINKEDIN_PROFILE_RE = re.compile(
    r"^https?://(?:www\.)?linkedin\.com/in/[^/?#\s]+/?", re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Query:
    """Parsed representation of a Q-block from wave1_linkedin_queries.md."""

    query_id: str
    cluster: str = ""
    boolean: str = ""
    industry_filter: str = ""
    location: str = "United States"
    expected_subtiers: list[str] = field(default_factory=list)
    why_this_slot: str = ""

    def is_runnable(self) -> bool:
        return bool(self.boolean) and "TODO" not in self.boolean


@dataclass
class SpiderResult:
    linkedin_profile_url: str
    title: str
    snippet: str


# ---------------------------------------------------------------------------
# .env.local loading (no python-dotenv dependency — keeps this stdlib-only)
# ---------------------------------------------------------------------------


def load_env_local(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


# ---------------------------------------------------------------------------
# Markdown query parser
# ---------------------------------------------------------------------------


def parse_queries(md_path: Path = QUERIES_FILE) -> dict[str, Query]:
    """Extract Q-blocks from the queries markdown file.

    Each block looks like:
        ### Q1 — WORKED EXAMPLE (overwrite if you want)
        - **Cluster:** OO-1 + OO-2
        - **Boolean:** ("VP Population Health" OR ...) AND (...)
        - **Industry filter:** Hospital & Health Care
        - **Location:** United States
        - **Expected subtiers:** 1A, 1C, 3A, 3B
        - **Why first:** ...

    Returns: dict keyed by query_id (e.g. "Q1").
    """
    text = md_path.read_text(encoding="utf-8")
    queries: dict[str, Query] = {}

    # Split on `### Q<id>` headers — id can be digits, letters, dashes, or
    # underscores (e.g., Q1, Q1A-OO, Q2B-PCL). Canonical generator uses the
    # subtier-role coded form.
    sections = re.split(r"^### (Q[\w-]+)[^\n]*$", text, flags=re.MULTILINE)
    # split returns: [preamble, "Q1", body1, "Q2", body2, ...]
    for i in range(1, len(sections), 2):
        qid = sections[i].strip()
        body = sections[i + 1] if i + 1 < len(sections) else ""
        q = Query(query_id=qid)

        for line in body.splitlines():
            line = line.strip()
            if not line.startswith("-"):
                continue
            line = line.lstrip("- ").strip()
            # Match patterns like **Field:** value
            m = re.match(r"\*\*([^:]+):\*\*\s*(.*)", line)
            if not m:
                continue
            field_name, value = m.group(1).strip().lower(), m.group(2).strip()

            # Strip backticks the user may have wrapped values in
            value = value.strip("`")

            if field_name == "cluster":
                q.cluster = value
            elif field_name == "boolean":
                q.boolean = value
            elif field_name == "industry filter":
                q.industry_filter = value
            elif field_name == "location":
                q.location = value or "United States"
            elif field_name == "expected subtiers":
                q.expected_subtiers = [s.strip() for s in value.split(",") if s.strip()]
            elif field_name in ("why first", "why this slot"):
                q.why_this_slot = value

        queries[qid] = q

    return queries


# ---------------------------------------------------------------------------
# Spider.cloud API call
# ---------------------------------------------------------------------------


def call_spider_search(boolean: str, api_key: str, search_limit: int = 30) -> list[SpiderResult]:
    """POST to Spider.cloud /search with the X-ray Boolean.

    crawl_results=False keeps this URL-cheap; we only want the search-result
    metadata (title, URL, snippet), not the full LinkedIn page contents.
    """
    full_query = f"{boolean} {LINKEDIN_PERSON_OPERATOR}"
    payload = {
        # Spider's live /search API expects 'search', not 'query' (the public
        # llms.txt docs are stale — the live error and live API examples
        # confirm 'search').
        "search": full_query,
        # search_limit is a CLI flag now — default 30, was hardcoded 10.
        # Higher = more raw results per call (linear cost increase).
        "search_limit": search_limit,
        # URL-only mode — just SERP metadata (url/title/snippet), not page
        # contents. Saves credits dramatically.
        "fetch_page_content": False,
        # quick_search prioritizes speed over fallback-search quantity. Our
        # queries are already maximally specific ("name" "org"), so we don't
        # need Spider to retry with looser variants.
        "quick_search": True,
        # lite_mode cuts data transfer cost ~50%. The trade-offs (slight geo
        # accuracy + reliability drop) don't affect us — we're not rendering
        # pages, just reading SERP results.
        "lite_mode": True,
    }
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        SPIDER_SEARCH_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=SPIDER_TIMEOUT_SECONDS) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        sys.stderr.write(
            f"[spider] HTTP {e.code} for query: {full_query[:80]}...\n"
            f"        response: {e.read().decode('utf-8', errors='replace')}\n"
        )
        return []
    except urllib.error.URLError as e:
        sys.stderr.write(f"[spider] URL error for query: {e.reason}\n")
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        sys.stderr.write(f"[spider] Non-JSON response: {raw[:200]}\n")
        return []

    results = _extract_results(data)
    if not results:
        # Diagnostic: when zero results come back, surface the response shape
        # AND look inside arrays for the actual item-level fields. This is
        # what tells us "the response had data but my parser missed the key."
        first_item: dict = {}
        if isinstance(data, list):
            shape = f"list of {len(data)} items"
            if data and isinstance(data[0], dict):
                first_item = data[0]
        elif isinstance(data, dict):
            shape = f"dict with keys: {list(data.keys())}"
            for k in ("content", "results", "data", "items"):
                v = data.get(k)
                if isinstance(v, list) and v and isinstance(v[0], dict):
                    first_item = v[0]
                    shape += f" (first list at '{k}' → {len(v)} items)"
                    break
        else:
            shape = type(data).__name__
        sys.stderr.write(
            f"[spider] zero parsed results — response shape: {shape}\n"
            f"        first-item keys: {list(first_item.keys()) if first_item else 'n/a'}\n"
            f"        raw preview: {raw[:400]}\n"
        )
    return results


def _extract_results(data) -> list[SpiderResult]:
    """Pull per-result fields out of the Spider /search response.

    Critical: Spider's /search returns a TOP-LEVEL ARRAY in URL-only mode —
    not a {results: [...]} object as the llms.txt docs imply. We accept both
    shapes defensively to survive future API changes.

    Filter to LinkedIn /in/ URLs only.
    """
    if isinstance(data, list):
        results_list = data
    elif isinstance(data, dict):
        # Spider's /search wraps results under "content" (verified live).
        # Other keys kept as defensive fallbacks for future API drift.
        results_list = (
            data.get("content")
            or data.get("results")
            or data.get("data")
            or data.get("items")
            or []
        )
    else:
        results_list = []

    out: list[SpiderResult] = []
    for r in results_list:
        if not isinstance(r, dict):
            continue
        url = (
            r.get("url")
            or r.get("link")
            or r.get("href")
            or ""
        )
        if not url or not LINKEDIN_PROFILE_RE.match(url):
            continue
        out.append(
            SpiderResult(
                linkedin_profile_url=url,
                title=r.get("title") or "",
                snippet=(
                    r.get("description")
                    or r.get("snippet")
                    or r.get("content")
                    or ""
                ),
            )
        )
    return out


# ---------------------------------------------------------------------------
# Dedup
# ---------------------------------------------------------------------------


def load_existing_urls(csv_path: Path = MASTER_CSV) -> set[str]:
    if not csv_path.exists():
        return set()
    urls: set[str] = set()
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = (row.get("linkedin_profile_url") or "").strip()
            if url:
                urls.add(_normalize_url(url))
    return urls


def _normalize_url(u: str) -> str:
    """Strip trailing slash, query, fragment so /in/john and /in/john/ dedupe."""
    u = u.split("?", 1)[0].split("#", 1)[0].rstrip("/")
    return u.lower()


# ---------------------------------------------------------------------------
# Output writer
# ---------------------------------------------------------------------------


def write_run_artifact(
    run_dir: Path,
    query: Query,
    raw_results: list[SpiderResult],
    new_results: list[SpiderResult],
) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    out_path = run_dir / f"{query.query_id}_raw_urls.json"
    payload = {
        "query_id": query.query_id,
        "query_string": f"{query.boolean} {LINKEDIN_PERSON_OPERATOR}".strip(),
        "industry_filter": query.industry_filter,
        "location": query.location,
        "expected_subtiers": query.expected_subtiers,
        "cluster": query.cluster,
        "why_this_slot": query.why_this_slot,
        "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "raw_result_count": len(raw_results),
        "deduped_result_count": len(new_results),
        "results": [
            {
                "linkedin_profile_url": r.linkedin_profile_url,
                "title": r.title,
                "snippet": r.snippet,
            }
            for r in new_results
        ],
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def run(query_ids: Optional[list[str]], dry_run: bool, queries_file: Path = QUERIES_FILE, search_limit: int = 30) -> int:
    load_env_local()
    api_key = os.environ.get("SPIDER_API_KEY", "").strip()
    if not api_key and not dry_run:
        sys.stderr.write("Missing SPIDER_API_KEY (set in .env.local)\n")
        return 2

    queries = parse_queries(queries_file)
    if not queries:
        sys.stderr.write(f"No queries parsed from {queries_file}\n")
        return 2

    if query_ids:
        unknown = [q for q in query_ids if q not in queries]
        if unknown:
            sys.stderr.write(f"Unknown query ids: {unknown}\n")
            return 2
        targets = [queries[q] for q in query_ids]
    else:
        targets = list(queries.values())

    runnable = [q for q in targets if q.is_runnable()]
    skipped = [q for q in targets if not q.is_runnable()]
    if skipped:
        sys.stderr.write(
            f"Skipping {len(skipped)} unfilled queries: "
            f"{', '.join(q.query_id for q in skipped)}\n"
        )
    if not runnable:
        sys.stderr.write("Nothing to run (all queries are TODOs).\n")
        return 1

    existing = load_existing_urls()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = RUNS_DIR / timestamp

    summary: list[tuple[str, int, int]] = []  # (qid, raw_count, new_count)

    for q in runnable:
        sys.stdout.write(f"[run] {q.query_id}: {q.boolean[:80]}...\n")
        if dry_run:
            summary.append((q.query_id, 0, 0))
            continue

        results = call_spider_search(q.boolean, api_key, search_limit=search_limit)
        new = [
            r for r in results
            if _normalize_url(r.linkedin_profile_url) not in existing
        ]
        # Track within-run dedup as well
        for r in new:
            existing.add(_normalize_url(r.linkedin_profile_url))

        out = write_run_artifact(run_dir, q, results, new)
        sys.stdout.write(
            f"      raw={len(results)} new={len(new)} → {out.relative_to(REPO_ROOT)}\n"
        )
        summary.append((q.query_id, len(results), len(new)))

        # Be polite to the API between calls
        time.sleep(0.5)

    # Print summary table
    sys.stdout.write("\n--- Run summary ---\n")
    for qid, raw, new in summary:
        sys.stdout.write(f"  {qid}: raw={raw}  new={new}\n")
    sys.stdout.write(f"  run dir: {run_dir.relative_to(REPO_ROOT)}\n")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--query",
        action="append",
        help="Run a specific query id (e.g. Q1). Repeatable.",
    )
    group.add_argument(
        "--all", action="store_true", help="Run every runnable query."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse queries but don't hit Spider.cloud.",
    )
    parser.add_argument(
        "--queries-file",
        default=str(QUERIES_FILE),
        help="Path to the Q-block markdown file. Defaults to fixtures/wave1_linkedin_queries.md.",
    )
    parser.add_argument(
        "--search-limit",
        type=int,
        default=30,
        help="Max results per Spider /search call. Default 30 (was 10).",
    )
    args = parser.parse_args()

    query_ids = args.query if args.query else None
    return run(
        query_ids,
        args.dry_run,
        queries_file=Path(args.queries_file),
        search_limit=args.search_limit,
    )


if __name__ == "__main__":
    sys.exit(main())
