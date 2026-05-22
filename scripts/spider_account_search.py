#!/usr/bin/env python3
"""Per-row Spider.cloud LinkedIn URL sourcer for the account-first pipeline.

Reads `fixtures/wave1_raw_accounts.csv`, builds one Spider query per row
based on `--mode`, calls Spider's /search endpoint, and writes results to a
JSONL checkpoint file (durable between runs) plus a final JSON file in the
schema `parallel_persona_extractor.py` expects.

Modes:
  2a-named   — uses Contact Name + Organization Name (high precision).
               Query: '"<contact>" "<org>"' (Spider appends site:linkedin.com/in)
               Best for 511 ACO rows where CMS provides exec contacts.

  1c-persona — uses Persona phrases + Organization Name. Runs ONE query per
               account that ORs the personas the user wants for that subtier.
               Query: '("<persona1>" OR "<persona2>") "<org>"'

Checkpoint behavior:
  After every row, appends a line to <out-jsonl>. On resume, the script
  counts lines in <out-jsonl> and skips that many input rows. So if bash
  kills the process mid-run, the next call picks up cleanly.

Usage:
  python3 scripts/spider_account_search.py --mode 2a-named --max-rows 5    # smoke
  python3 scripts/spider_account_search.py --mode 2a-named                  # full
  python3 scripts/spider_account_search.py --mode 1c-persona --max-rows 100 # 1C subset

Required env: SPIDER_API_KEY (loaded from .env.local).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Reuse Spider call + LinkedIn URL filter from the existing runner.
from scripts.spider_query_runner import (  # noqa: E402
    LINKEDIN_PERSON_OPERATOR,
    SPIDER_SEARCH_URL,
    SpiderResult,
    _extract_results,
    call_spider_search,
    load_env_local,
)

ACCOUNTS_CSV = REPO_ROOT / "fixtures" / "wave1_raw_accounts.csv"
RUNS_DIR = REPO_ROOT / "fixtures" / "wave1_runs"

# Personas to OR per 1C account (provider-wedge connection-request batch).
PERSONA_TITLES_1C = [
    "Practice Administrator",
    "Practice Manager",
    "Director of Operations",
    "Medical Director",
    "Chief Medical Officer",
    "CMO",
]

# 1A persona set — same titles as 1C; mid-market PCP groups share the same
# decision-maker roles. Defined separately so they can diverge if needed.
PERSONA_TITLES_1A = PERSONA_TITLES_1C

# 2A BH-purpose persona set. Inverts the standard 2A search: instead of
# searching for a named CMS contact at an ACO and asking "is this person
# BH-aligned?", we search the ACO org for any person with a behavioral-health
# title. Targets the user's "BH-purpose decision maker" hypothesis.
#
# Capped at 3 OR-terms: Spider/Google returns empty content above 3 ORs in
# most query length bands (verified 2026-05-21 — 3-OR=20 hits, 4-OR=0,
# 5-OR=20, 6-OR=0). Picking the 3 highest-prevalence BH leadership titles
# covers the standard ops lead, senior exec, and physician-executive variants;
# adjacent titles (Chief BH Officer, BH Director, etc.) still surface in the
# matched profiles' snippets and can be detected in downstream scoring.
PERSONA_TITLES_2A_BH = [
    "Director of Behavioral Health",
    "VP Behavioral Health",
    "Behavioral Health Medical Director",
]

# 2A ACO buying-persona set — the three highest-yield titles for Kivira's
# value prop at an ACO (collaborative care decision support, BH workflow,
# pop-health quality improvement). Same 3-OR cap as BH mode. Picks one
# title per primary persona bucket:
#   - VP Population Health         → Operational Owner (highest-prevalence)
#   - Director of Population Health→ Operational Owner alt (mid-level)
#   - CMO                          → Clinical Champion
# Other personas (CFO/CEO, Director of Analytics, BH/Quality Influencer)
# are covered by separate queries — see PERSONA_TITLES_2A_BH for BH and
# the planned `2a-econ-persona` mode for econ-buyer titles if needed.
PERSONA_TITLES_2A_ACO = [
    "VP Population Health",
    "Director of Population Health",
    "CMO",
]

# Tokens too generic to be useful for matching. Most ACO/practice names contain
# at least one of these — including them in the org-match would inflate scores
# meaninglessly. Keep "medical" and "group" because they ARE discriminative.
STOPWORDS = {
    "llc", "inc", "pa", "pc", "ltd", "llp", "the", "and", "of", "co",
    "corp", "corporation", "company", "or",
}


def tokenize(text: str) -> list[str]:
    """Lowercase + strip non-alpha + drop stopwords + drop tokens shorter than 3 chars."""
    import re as _re
    raw = _re.findall(r"[a-z]+", (text or "").lower())
    return [t for t in raw if len(t) >= 3 and t not in STOPWORDS]


def score_hit(
    hit: dict,
    identity_tokens: list[str],
    org_tokens: list[str],
    min_identity_matches: int = 1,
    min_org_matches: int = 1,
) -> int:
    """Score a Spider SERP hit against the query's identity + org tokens.

    Returns -1 (disqualified) if either group has fewer matches than its floor.
    Otherwise returns total distinct-token matches across URL slug + title +
    snippet. Higher = better.

    Why two groups: a single combined score lets "right name, wrong company"
    hits pass — e.g., the 8 Karen Holts at random orgs we saw in the smoke run.
    Splitting identity vs. org enforces 'must be a real match on both sides.'
    """
    blob = " ".join([
        hit.get("linkedin_profile_url", ""),
        hit.get("title", ""),
        hit.get("snippet", ""),
    ]).lower()
    id_matches = sum(1 for t in set(identity_tokens) if t in blob)
    org_matches = sum(1 for t in set(org_tokens) if t in blob)
    if id_matches < min_identity_matches or org_matches < min_org_matches:
        return -1
    return id_matches + org_matches


def rank_and_take_top_n(
    hits: list[dict],
    identity_tokens: list[str],
    org_tokens: list[str],
    top_n: int,
    min_identity_matches: int = 1,
    min_org_matches: int = 1,
) -> list[dict]:
    """Apply score_hit to every hit, drop disqualified, sort by score desc, take top N."""
    scored: list[tuple[int, dict]] = []
    for h in hits:
        s = score_hit(h, identity_tokens, org_tokens, min_identity_matches, min_org_matches)
        if s >= 0:
            scored.append((s, h))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{**h, "_match_score": s} for s, h in scored[:top_n]]


def build_query(row: dict, mode: str) -> str | None:
    """Construct the Spider Boolean for one account row.

    For 2a-named: requires both contact name and org name.
    For 1c-persona: requires org name only (personas are baked in).
    Returns None when the row has insufficient signal.
    """
    org = (row.get("Organization Name") or "").strip()
    if not org:
        return None
    if mode == "2a-named":
        contact = (row.get("Contact Name") or "").strip()
        if not contact:
            return None
        # Quote both — search engines treat quoted strings as exact phrases.
        return f'"{contact}" "{org}"'
    if mode == "1c-persona":
        personas_or = " OR ".join(f'"{p}"' for p in PERSONA_TITLES_1C)
        return f'({personas_or}) "{org}"'
    if mode == "1a-persona":
        personas_or = " OR ".join(f'"{p}"' for p in PERSONA_TITLES_1A)
        return f'({personas_or}) "{org}"'
    if mode == "2a-bh-persona":
        personas_or = " OR ".join(f'"{p}"' for p in PERSONA_TITLES_2A_BH)
        return f'({personas_or}) "{org}"'
    if mode == "2a-aco-persona":
        personas_or = " OR ".join(f'"{p}"' for p in PERSONA_TITLES_2A_ACO)
        return f'({personas_or}) "{org}"'
    raise ValueError(f"unknown mode: {mode}")


def row_subtier(row: dict) -> str:
    """Pull subtier code out of Internal Notes ('wave=1; subtier=2A; source=...')."""
    notes = row.get("Internal Notes", "") or ""
    for part in notes.split(";"):
        part = part.strip()
        if part.startswith("subtier="):
            return part.split("=", 1)[1].strip()
    return ""


def filter_accounts_for_mode(rows: list[dict], mode: str) -> list[dict]:
    """Pick only the rows that match the mode's tier."""
    if mode == "2a-named":
        return [r for r in rows if row_subtier(r) == "2A"]
    if mode == "1c-persona":
        return [r for r in rows if row_subtier(r) == "1C"]
    if mode == "1a-persona":
        return [r for r in rows if row_subtier(r) == "1A"]
    if mode == "2a-bh-persona":
        return [r for r in rows if row_subtier(r) == "2A"]
    if mode == "2a-aco-persona":
        return [r for r in rows if row_subtier(r) == "2A"]
    return rows


def load_done_indices(jsonl_path: Path) -> set[int]:
    """Indices of accounts already processed (so we can resume)."""
    if not jsonl_path.exists():
        return set()
    done: set[int] = set()
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            idx = obj.get("_account_index")
            if isinstance(idx, int):
                done.add(idx)
    return done


def write_jsonl_record(jsonl_path: Path, record: dict) -> None:
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def collate_jsonl_to_q_json(
    jsonl_path: Path,
    out_json: Path,
    query_id: str,
    mode: str,
    top_n: int = 1,
    min_id_matches: int = 1,
    min_org_matches: int = 1,
    shuffle: bool = False,
    shuffle_seed: int | None = None,
) -> int:
    """Convert JSONL checkpoint → final Q*_raw_urls.json with precision filter.

    For each account record in the JSONL, score every hit against the
    identity + org tokens, take top-N by score, then dedup across accounts.
    """
    import random as _random
    seen: set[str] = set()
    results: list[dict] = []
    per_account_kept = []  # for diagnostics

    with jsonl_path.open("r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]

    if shuffle:
        rng = _random.Random(shuffle_seed) if shuffle_seed is not None else _random.Random()
        rng.shuffle(records)

    for obj in records:
        org_name = obj.get("org", "")
        org_tokens = tokenize(org_name)

        # Identity tokens depend on the search mode the row was captured under.
        if mode == "2a-named":
            identity = obj.get("contact_name", "")
            identity_tokens = tokenize(identity)
        elif mode in ("1c-persona", "1a-persona", "2a-bh-persona", "2a-aco-persona"):
            # Use the persona phrases as the identity tokens — at least one
            # must appear in title/snippet for the hit to qualify.
            titles = {
                "1c-persona": PERSONA_TITLES_1C,
                "1a-persona": PERSONA_TITLES_1A,
                "2a-bh-persona": PERSONA_TITLES_2A_BH,
                "2a-aco-persona": PERSONA_TITLES_2A_ACO,
            }[mode]
            identity_tokens = []
            for p in titles:
                identity_tokens.extend(tokenize(p))
        else:
            identity_tokens = []

        ranked = rank_and_take_top_n(
            obj.get("hits", []),
            identity_tokens=identity_tokens,
            org_tokens=org_tokens,
            top_n=top_n,
            min_identity_matches=min_id_matches,
            min_org_matches=min_org_matches,
        )

        # Persona-mode precision tightening for 2A modes. tokenize() splits
        # multi-word title patterns ("VP Population Health" → "vp" dropped,
        # "population" + "health") and strips healthcare-generic org words,
        # which lets cross-org name collisions through (Michael Paustian @
        # Trinity Health matching the Abacus Health LLC ACO because "health"
        # is shared). Two layered filters address this:
        #
        # 1. Distinctive-org-token (brand) match — require the longest
        #    non-generic org token (e.g. "abacus" from "Abacus Health LLC",
        #    "adventhealth" from "AdventHealth ACO") to appear in the
        #    candidate's URL/title/snippet blob.
        # 2. BH semantic anchor (BH mode only) — require literal "behavioral"
        #    or "mental" in title/snippet so generic "Director at Health Co"
        #    titles don't pass.
        if mode in ("2a-bh-persona", "2a-aco-persona"):
            # Pick the most distinctive ("brand") token: the longest token
            # that isn't a generic healthcare/org word.
            BH_GENERIC = {
                "health", "healthcare", "care", "medical", "medicine",
                "clinical", "services", "service", "partners", "partner",
                "network", "networks", "associates", "association",
                "physicians", "physician", "hospital", "hospitals", "clinic",
                "clinics", "consultation", "management", "solutions",
                "coalition", "accountable", "organization", "professional",
                "group", "alliance", "system", "systems", "wellness",
                "primary", "community", "regional", "national", "integrated",
                "advanced", "premier", "select", "performance",
            }
            org_tokens_local = sorted(
                (t for t in org_tokens if t not in BH_GENERIC),
                key=len, reverse=True,
            )
            distinctive = org_tokens_local[0] if org_tokens_local else None

            def _passes_persona_filters(h: dict) -> bool:
                blob = " ".join([
                    h.get("linkedin_profile_url", ""),
                    h.get("title", ""),
                    h.get("snippet", ""),
                ]).lower()
                if mode == "2a-bh-persona":
                    if ("behavioral" not in blob
                            and "mental " not in blob
                            and "mental-" not in blob):
                        return False
                if distinctive and distinctive not in blob:
                    return False
                return True

            ranked = [h for h in ranked if _passes_persona_filters(h)]

        per_account_kept.append((org_name, len(obj.get("hits", [])), len(ranked)))

        for hit in ranked:
            url = (hit.get("linkedin_profile_url") or "").strip().rstrip("/")
            if not url or url.lower() in seen:
                continue
            seen.add(url.lower())
            results.append(
                {
                    "linkedin_profile_url": url,
                    "title": hit.get("title", ""),
                    "snippet": hit.get("snippet", ""),
                    "match_score": hit.get("_match_score", 0),
                    "source_account": org_name,
                    "source_state": obj.get("state", ""),
                    "source_subtier": obj.get("subtier", ""),
                }
            )
    # Set top-level subtier label on the JSON file itself.
    expected_subtiers = {
        "2a-named": ["2A"],
        "1c-persona": ["1C"],
        "1a-persona": ["1A"],
        "2a-bh-persona": ["2A"],
        "2a-aco-persona": ["2A"],
    }.get(mode, [mode])
    payload = {
        "query_id": query_id,
        "query_string": f"per-row {mode} (Spider /search + {LINKEDIN_PERSON_OPERATOR})",
        "industry_filter": "(N/A — account-first sourcing)",
        "location": "United States",
        "expected_subtiers": expected_subtiers,
        "cluster": f"per-row sourcing mode={mode}",
        "why_this_slot": "Account-first: subtier known from CMS source, only persona/contact varies per row.",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "raw_result_count": len(results),
        "deduped_result_count": len(results),
        "results": results,
    }
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return len(results)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["2a-named", "1c-persona", "1a-persona", "2a-bh-persona", "2a-aco-persona"], required=True)
    p.add_argument("--accounts-csv", default=str(ACCOUNTS_CSV))
    p.add_argument(
        "--run-dir",
        help="Run dir name under fixtures/wave1_runs/. Defaults to a new UTC timestamp.",
    )
    p.add_argument("--max-rows", type=int, default=0, help="0 = process all remaining.")
    p.add_argument("--query-id", default=None)
    p.add_argument("--per-call-sleep", type=float, default=0.4)
    # Precision filter (applied during collation):
    p.add_argument("--top-n", type=int, default=1, help="Per-account top hits to keep after scoring.")
    p.add_argument("--min-id-matches", type=int, default=1)
    p.add_argument("--min-org-matches", type=int, default=1)
    p.add_argument("--shuffle", action="store_true", help="Randomize record order in final JSON (raffle/anti-bot).")
    p.add_argument("--shuffle-seed", type=int, default=None, help="Set for reproducible shuffle.")
    p.add_argument("--collate-only", action="store_true", help="Skip Spider calls, just re-collate existing JSONL with current filter settings.")
    p.add_argument("--concurrency", type=int, default=1, help="Number of concurrent Spider calls (ThreadPoolExecutor workers).")
    args = p.parse_args()

    load_env_local()
    api_key = os.environ.get("SPIDER_API_KEY", "").strip()
    if not api_key:
        sys.stderr.write("Missing SPIDER_API_KEY in .env.local\n")
        return 2

    # Resolve / create run dir.
    if args.run_dir:
        run_dir = RUNS_DIR / args.run_dir
    else:
        run_dir = RUNS_DIR / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir.mkdir(parents=True, exist_ok=True)

    _default_qid = {"2a-named": "Q2A", "1c-persona": "Q1C", "1a-persona": "Q1A", "2a-bh-persona": "Q2A_BH", "2a-aco-persona": "Q2A_ACO"}
    query_id = args.query_id or _default_qid.get(args.mode, "Q_UNKNOWN")
    jsonl_path = run_dir / f"{query_id}_progress.jsonl"
    out_json = run_dir / f"{query_id}_raw_urls.json"

    # Load + filter accounts.
    with Path(args.accounts_csv).open("r", encoding="utf-8-sig", newline="") as f:
        all_accounts = list(csv.DictReader(f))
    accounts = filter_accounts_for_mode(all_accounts, args.mode)
    if not accounts:
        sys.stderr.write(f"No accounts match mode={args.mode}\n")
        return 1

    done = load_done_indices(jsonl_path)
    todo = [(i, a) for i, a in enumerate(accounts) if i not in done]
    sys.stdout.write(
        f"[spider-account] mode={args.mode} run={run_dir.name} "
        f"total={len(accounts)} done={len(done)} todo={len(todo)}\n"
    )

    if args.collate_only:
        sys.stdout.write("[spider-account] --collate-only: skipping all Spider calls\n")
        todo = []
    elif args.max_rows > 0:
        todo = todo[: args.max_rows]
        sys.stdout.write(f"[spider-account] this batch will process {len(todo)} rows\n")

    processed = 0
    total_hits = 0

    def process_one(idx_row):
        idx, row = idx_row
        boolean = build_query(row, args.mode)
        if not boolean:
            return {
                "_account_index": idx,
                "org": row.get("Organization Name", ""),
                "state": row.get("State Code", ""),
                "subtier": row_subtier(row),
                "skipped_reason": "insufficient signal (missing org or contact)",
                "hits": [],
            }
        results = call_spider_search(boolean, api_key)
        hits = [
            {
                "linkedin_profile_url": r.linkedin_profile_url,
                "title": r.title,
                "snippet": r.snippet,
            }
            for r in results
        ]
        return {
            "_account_index": idx,
            "org": row.get("Organization Name", ""),
            "state": row.get("State Code", ""),
            "subtier": row_subtier(row),
            "contact_name": row.get("Contact Name", ""),
            "query": boolean,
            "hit_count": len(hits),
            "hits": hits,
        }

    if args.concurrency > 1 and todo:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        # Lock for serialized JSONL writes (file append is atomic per write but
        # we want to avoid interleaved writes if Python were to swap mid-write).
        import threading
        write_lock = threading.Lock()
        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            futures = {ex.submit(process_one, ir): ir for ir in todo}
            for fut in as_completed(futures):
                rec = fut.result()
                with write_lock:
                    write_jsonl_record(jsonl_path, rec)
                processed += 1
                total_hits += rec.get("hit_count", 0)
    else:
        for ir in todo:
            rec = process_one(ir)
            write_jsonl_record(jsonl_path, rec)
            processed += 1
            total_hits += rec.get("hit_count", 0)
            if args.per_call_sleep > 0:
                time.sleep(args.per_call_sleep)

    sys.stdout.write(
        f"[spider-account] processed={processed}  total_hits={total_hits}  "
        f"jsonl={jsonl_path.relative_to(REPO_ROOT)}\n"
    )

    # Always rewrite the final JSON from the JSONL — this is cheap and ensures
    # the file reflects every row processed so far, even partial runs.
    final_count = collate_jsonl_to_q_json(
        jsonl_path,
        out_json,
        query_id,
        args.mode,
        top_n=args.top_n,
        min_id_matches=args.min_id_matches,
        min_org_matches=args.min_org_matches,
        shuffle=args.shuffle,
        shuffle_seed=args.shuffle_seed,
    )
    sys.stdout.write(
        f"[spider-account] collated {final_count} unique LinkedIn URLs → "
        f"{out_json.relative_to(REPO_ROOT)}\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
