#!/usr/bin/env python3
"""Parallel.ai persona extractor — Wave 1 LinkedIn enrichment.

Reads JSON files from `fixtures/wave1_runs/<timestamp>/Q*_raw_urls.json`,
fans them out to Parallel.ai's Task Group API, and writes structured
results into `fixtures/wave1_linkedin_master.csv` (appending, deduped).

For each LinkedIn URL the task extracts:
- firstName, lastName
- current_title, current_company
- persona_guess (using PERSONA_DEFINITIONS from tam_builder.persona_rules)
- subtier_guess (heuristic from company name)
- signal_score (heuristic from public profile data)
- confidence (high|medium|low) — gated for HeyReach load

The `tag_persona()` keyword path runs first per row; only `unknown` rows
are sent to the LLM (saves Parallel credits).

Usage:
    python scripts/parallel_persona_extractor.py --run 20260501T181152Z
    python scripts/parallel_persona_extractor.py --latest
    python scripts/parallel_persona_extractor.py --latest --processor base

Required env:
    PARALLEL_API_KEY (loaded from .env.local)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

# Project imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tam_builder.persona_rules import (  # noqa: E402
    PERSONA_DEFINITIONS,
    refine_subtier_1a,
    tag_persona_keyword,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = REPO_ROOT / "fixtures" / "wave1_runs"
MASTER_CSV = REPO_ROOT / "fixtures" / "wave1_linkedin_master.csv"
ENV_FILE = REPO_ROOT / ".env.local"

PARALLEL_API_BASE = "https://api.parallel.ai"
# Task-group orchestration (submit, poll, manage): /v1beta/tasks/groups
PARALLEL_TASK_GROUPS = f"{PARALLEL_API_BASE}/v1beta/tasks/groups"
# Per-run results live on the run itself, NOT under the taskgroup:
#   GET /v1/tasks/runs/{run_id}/result
PARALLEL_RUN_RESULT = f"{PARALLEL_API_BASE}/v1/tasks/runs"
PARALLEL_TIMEOUT_SECONDS = 60

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
# .env loader
# ---------------------------------------------------------------------------


def load_env_local(path: Path = ENV_FILE) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


# ---------------------------------------------------------------------------
# Run discovery
# ---------------------------------------------------------------------------


def latest_run_dir() -> Optional[Path]:
    """Return the most recent real run directory.

    Skips TEST_* and _* prefixed dirs so dev fixtures don't pollute --latest.
    """
    if not RUNS_DIR.exists():
        return None
    runs = sorted(
        p for p in RUNS_DIR.iterdir()
        if p.is_dir() and not p.name.startswith(("TEST_", "_"))
    )
    return runs[-1] if runs else None


def collect_urls(run_dir: Path) -> list[dict]:
    """Read every Q*_raw_urls.json in run_dir and return a flat list of
    {linkedin_profile_url, source_query, expected_subtiers, snippet, title}.
    """
    rows: list[dict] = []
    for f in sorted(run_dir.glob("Q*_raw_urls.json")):
        payload = json.loads(f.read_text(encoding="utf-8"))
        for r in payload.get("results", []):
            rows.append(
                {
                    "linkedin_profile_url": r["linkedin_profile_url"],
                    "source_query": payload["query_id"],
                    "expected_subtiers": payload.get("expected_subtiers", []),
                    "snippet": r.get("snippet", ""),
                    "search_title": r.get("title", ""),
                }
            )
    return rows


# ---------------------------------------------------------------------------
# Master CSV — read existing URLs for dedup, write new rows on append
# ---------------------------------------------------------------------------


def load_existing_urls(csv_path: Path = MASTER_CSV) -> set[str]:
    if not csv_path.exists():
        return set()
    urls: set[str] = set()
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = (row.get("linkedin_profile_url") or "").strip().lower().rstrip("/")
            if url:
                urls.add(url)
    return urls


def validate_master_csv_header(path: Path = MASTER_CSV) -> None:
    """Refuse to append if an existing file's header does not match CSV_HEADERS."""
    if not path.exists() or path.stat().st_size == 0:
        return
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        first = next(reader, None)
    if first is None:
        return
    if list(first) != CSV_HEADERS:
        raise ValueError(
            "wave1_linkedin_master.csv header mismatch — delete the file or "
            "rewrite its header to match scripts/parallel_persona_extractor.CSV_HEADERS.\n"
            f"Expected: {CSV_HEADERS}\nGot:      {first}"
        )


def append_master(rows: list[dict]) -> None:
    """Append rows to master CSV, creating header if missing."""
    validate_master_csv_header()
    write_header = not MASTER_CSV.exists() or MASTER_CSV.stat().st_size == 0
    MASTER_CSV.parent.mkdir(parents=True, exist_ok=True)
    with MASTER_CSV.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if write_header:
            writer.writeheader()
        for row in rows:
            writer.writerow({h: row.get(h, "") for h in CSV_HEADERS})


# ---------------------------------------------------------------------------
# Parallel.ai task spec
# ---------------------------------------------------------------------------


def build_task_spec() -> dict:
    """Define the input/output schema for the Parallel task group.

    SLIM SCHEMA (5 properties) — Parallel's base processor recommends ≤5
    output properties. Activity signals (posts/connections/photo) were
    dropped because LinkedIn blocks unauthenticated bots from reading them
    anyway. We rely on Spider's snippet text + the LLM to extract just the
    floor signals: who they are, what they do, who they work for, and which
    of the 9 Kivira subtiers their employer fits.

    Input: linkedin_url + search_snippet (Spider's SERP description).
    """
    persona_block = "\n".join(
        f"- {k}: {v}" for k, v in PERSONA_DEFINITIONS.items()
    )

    output_props = {
        "full_name": {
            "type": "string",
            "description": "Full name as it appears on the LinkedIn profile.",
        },
        "current_title": {
            "type": "string",
            "description": "Current job title.",
        },
        "current_company": {
            "type": "string",
            "description": "Current employer name.",
        },
        "persona": {
            "type": "string",
            "description": (
                "One of: operational_owner, clinical_champion, economic_buyer, "
                "tech_gatekeeper, bh_quality_influencer, unknown.\n"
                "Definitions:\n" + persona_block
            ),
        },
        "subtier_guess": {
            "type": "string",
            "description": (
                "Which of Kivira's 9 subtiers does the employer fit? "
                "1A (mid-market provider group), 1B (PCP group), "
                "1C (VBC provider group), 2A (ACO), 2B (VBC enablement), "
                "2C (care management co.), 3A (health system), 3B (IDN), "
                "3C (regional payer), or unknown."
            ),
        },
    }

    return {
        "input_schema": {
            "type": "json",
            "json_schema": {
                "type": "object",
                "properties": {
                    "linkedin_url": {"type": "string"},
                    "search_snippet": {"type": "string"},
                },
                "required": ["linkedin_url"],
            },
        },
        "output_schema": {
            "type": "json",
            "json_schema": {
                "type": "object",
                "properties": output_props,
                "required": [
                    "current_title",
                    "current_company",
                    "persona",
                    "subtier_guess",
                ],
            },
        },
    }


# ---------------------------------------------------------------------------
# Signal score — TODO: Keegan, this is your ~10-line weighting decision
# ---------------------------------------------------------------------------


def compute_signal_score(
    persona: str,
    persona_confidence: str,
    subtier_guess: str,
) -> int:
    """Score 0-100. Title/company-based signal only.

    SLIM SCHEMA VERSION — LinkedIn activity signals were dropped because
    LinkedIn blocks unauthenticated bots from reading them, AND the base
    processor recommends ≤5 schema properties. The score now reflects
    "can this person plausibly fit one of our 9 subtiers and 5 personas?"

      +20  persona is recognized (any non-'unknown')
      +30  persona == 'bh_quality_influencer' (warmest for our wedge)
      +10  persona_confidence == 'high' (keyword classifier matched)
      +10  subtier_guess is a real subtier code (1A...3C, not 'unknown')

    Max score: 70 (BH Director at a clearly-tagged 1A/1B/etc.)
    Min for any non-unknown persona: 30 (clears threshold of 25).
    Pure 'unknown' floors at 0 (parked).
    """
    score = 0
    if persona != "unknown":
        score += 20
    if persona == "bh_quality_influencer":
        score += 30
    if persona_confidence == "high":
        score += 10
    if subtier_guess and subtier_guess.lower() != "unknown":
        score += 10
    return min(100, score)


# 25 = threshold; any recognized persona at high keyword confidence passes
# (20 + 10 = 30). Drop to 15 if you want even unmatched-confidence personas in.
SIGNAL_SCORE_LOAD_THRESHOLD = 25


# ---------------------------------------------------------------------------
# Parallel.ai HTTP wiring
# ---------------------------------------------------------------------------


def _post_json(url: str, payload: dict, api_key: str) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=PARALLEL_TIMEOUT_SECONDS) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(url: str, api_key: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={"x-api-key": api_key, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=PARALLEL_TIMEOUT_SECONDS) as resp:
        return json.loads(resp.read().decode("utf-8"))


def submit_task_group(
    rows: list[dict], processor: str, api_key: str
) -> tuple[str, list[str], dict[str, dict]]:
    """Create a task group and add one task per row.

    Returns (taskgroup_id, run_ids, run_id_to_seed_map). The seed map
    bridges fan-out → fan-in: Parallel returns run_ids in the same order
    as our submitted inputs, so we zip them to recover the original
    LinkedIn URL when fetching results (the result endpoint doesn't
    echo back the input).
    """
    task_spec = build_task_spec()
    create = _post_json(PARALLEL_TASK_GROUPS, {}, api_key)
    taskgroup_id = create.get("taskgroup_id") or create.get("id") or create.get("group_id")
    if not taskgroup_id:
        raise RuntimeError(f"Could not parse taskgroup_id from: {create}")

    add_payload = {
        "default_task_spec": task_spec,
        "inputs": [
            {
                "input": {
                    "linkedin_url": r["linkedin_profile_url"],
                    "search_snippet": r.get("snippet", ""),
                },
                "processor": processor,
            }
            for r in rows
        ],
    }
    add_resp = _post_json(
        f"{PARALLEL_TASK_GROUPS}/{taskgroup_id}/runs",
        add_payload,
        api_key,
    )
    run_ids = add_resp.get("run_ids") or []
    if not run_ids:
        sys.stderr.write(
            f"[warn] no run_ids in add-runs response: {add_resp}\n"
        )
        return taskgroup_id, [], {}

    # Zip run_ids to seed rows so we can recover linkedin_url after fetch.
    if len(run_ids) != len(rows):
        sys.stderr.write(
            f"[warn] run_ids length ({len(run_ids)}) != rows length "
            f"({len(rows)}) — alignment may be off\n"
        )
    run_id_to_seed = {
        rid: rows[i] for i, rid in enumerate(run_ids) if i < len(rows)
    }
    return taskgroup_id, run_ids, run_id_to_seed


def wait_for_completion(taskgroup_id: str, api_key: str, poll_seconds: int = 10) -> None:
    while True:
        info = _get_json(
            f"{PARALLEL_TASK_GROUPS}/{taskgroup_id}", api_key
        )
        status = info.get("status", {})
        is_active = status.get("is_active", True)
        counts = status.get("task_run_status_counts", {})
        sys.stdout.write(f"  [poll] {counts}\n")
        if not is_active:
            return
        time.sleep(poll_seconds)


def _extract_content(evt: dict) -> tuple[Optional[dict], Optional[str]]:
    """Pull structured content out of a Parallel run-result response.

    The /result endpoint returns one of two shapes:
      A. Wrapped: {"run": {...}, "output": {"content": "...", "type": "json"}}
         — content may be a JSON string OR an object
      B. Flat: {"founding_date": "...", "field2": "..."} — the structured
         fields directly at the top level

    Returns (content_dict, drop_reason).
    """
    if not isinstance(evt, dict):
        return None, "evt-not-dict"

    # Shape A — output is wrapped
    out_raw = evt.get("output")
    content: object = None
    if isinstance(out_raw, dict):
        for key in ("content", "parsed", "data", "result"):
            v = out_raw.get(key)
            if v is not None:
                content = v
                break
        if content is None:
            # output dict itself might BE the content (no nested 'content' key)
            non_meta_keys = {k for k in out_raw if k not in ("type", "basis", "citations")}
            if non_meta_keys:
                content = {k: out_raw[k] for k in non_meta_keys}
    elif isinstance(out_raw, str):
        content = out_raw

    # Shape B — top-level fields are the structured output
    if content is None:
        non_meta_keys = {
            k for k in evt
            if k not in ("run", "output", "metadata", "run_id", "interaction_id",
                         "status", "is_active", "warnings", "error", "processor",
                         "taskgroup_id", "created_at", "modified_at", "type", "basis")
        }
        if non_meta_keys:
            content = {k: evt[k] for k in non_meta_keys}

    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            return None, "content-string-not-json"

    if not isinstance(content, dict):
        return None, "content-not-dict"

    return content, None


def fetch_results(
    run_ids: list[str], api_key: str
) -> Iterable[tuple[str, dict]]:
    """Fetch each run's result via /v1/tasks/runs/{run_id}/result.

    Yields (run_id, result_dict) so the caller can map back to seed rows.
    """
    for rid in run_ids:
        url = f"{PARALLEL_RUN_RESULT}/{rid}/result"
        try:
            yield rid, _get_json(url, api_key)
        except urllib.error.HTTPError as e:
            sys.stderr.write(
                f"[warn] HTTP {e.code} fetching run {rid}: "
                f"{e.read().decode('utf-8', errors='replace')[:200]}\n"
            )
        except Exception as e:
            sys.stderr.write(f"[warn] failed to fetch run {rid}: {e}\n")


# ---------------------------------------------------------------------------
# Row construction
# ---------------------------------------------------------------------------


def build_master_row(
    seed: dict, llm_output: dict, today_iso: str
) -> dict:
    title = (llm_output.get("current_title") or "").strip()
    company = (llm_output.get("current_company") or "").strip()
    full_name = (llm_output.get("full_name") or "").strip()

    # Keyword path first (includes disqualifiers). High confidence = matched
    # persona OR confidently-not-buyer (disqualified) — do not override with LLM.
    kw = tag_persona_keyword(title, company)
    if kw["confidence"] == "high":
        persona = kw["persona"]
        persona_confidence = kw["confidence"]
        persona_rationale = kw["rationale"]
    else:
        persona = (llm_output.get("persona") or "unknown").strip()
        persona_confidence = "medium" if persona != "unknown" else "low"
        persona_rationale = "llm-judgment"

    subtier_raw = (llm_output.get("subtier_guess") or "unknown").strip()
    subtier, subtier_confidence = refine_subtier_1a(subtier_raw, company)
    signal = compute_signal_score(persona, persona_confidence, subtier)

    return {
        "linkedin_profile_url": seed["linkedin_profile_url"],
        "full_name": full_name,
        "current_title": title,
        "current_company": company,
        "persona": persona,
        "persona_confidence": persona_confidence,
        "persona_rationale": persona_rationale,
        "subtier_guess": subtier,
        "subtier_confidence": subtier_confidence,
        "signal_score": signal,
        "location": "",
        "source_query": seed.get("source_query", ""),
        "date_captured": today_iso,
        "heyreach_campaign": "",  # set by Task 4 loader
        "notes": "",
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run(run_dir: Path, processor: str, dry_run: bool) -> int:
    load_env_local()
    api_key = os.environ.get("PARALLEL_API_KEY", "").strip()
    if not api_key and not dry_run:
        sys.stderr.write("Missing PARALLEL_API_KEY (set in .env.local)\n")
        return 2

    sys.stdout.write(f"[extract] reading {run_dir.relative_to(REPO_ROOT)}\n")
    seeds = collect_urls(run_dir)
    if not seeds:
        sys.stderr.write("No URLs found in run dir.\n")
        return 1

    existing = load_existing_urls()
    fresh = [s for s in seeds if s["linkedin_profile_url"].lower().rstrip("/") not in existing]
    sys.stdout.write(f"[extract] {len(seeds)} total, {len(fresh)} new after dedup\n")
    if not fresh:
        sys.stdout.write("[extract] nothing new to process\n")
        return 0

    if dry_run:
        sys.stdout.write(f"[extract] DRY RUN — would submit {len(fresh)} URLs to Parallel processor={processor}\n")
        return 0

    sys.stdout.write(f"[extract] submitting task group (processor={processor})...\n")
    tg_id, run_ids, run_id_to_seed = submit_task_group(fresh, processor, api_key)
    sys.stdout.write(f"[extract] taskgroup_id={tg_id}  runs_submitted={len(run_ids)}\n")
    if not run_ids:
        return 1

    wait_for_completion(tg_id, api_key)

    sys.stdout.write(f"[extract] fetching results for {len(run_ids)} runs...\n")
    today = datetime.now(timezone.utc).date().isoformat()
    new_rows: list[dict] = []
    fetched = 0
    parsed = 0
    first_evt: Optional[dict] = None
    drop_reason_counts: dict[str, int] = {}
    for run_id, evt in fetch_results(run_ids, api_key):
        fetched += 1
        if first_evt is None:
            first_evt = evt

        seed = run_id_to_seed.get(run_id)
        if seed is None:
            drop_reason_counts["unmapped-run-id"] = drop_reason_counts.get("unmapped-run-id", 0) + 1
            continue

        content, drop_reason = _extract_content(evt)
        if drop_reason or content is None:
            drop_reason_counts[drop_reason or "no-content"] = (
                drop_reason_counts.get(drop_reason or "no-content", 0) + 1
            )
            continue

        new_rows.append(build_master_row(seed, content, today))
        parsed += 1

    sys.stdout.write(f"[extract] fetched={fetched}  parsed={parsed}\n")
    if drop_reason_counts:
        sys.stdout.write(f"[extract] drop reasons: {drop_reason_counts}\n")

    # Diagnostic: when nothing parsed, dump the first run shape so we can patch
    if fetched > 0 and parsed == 0 and first_evt is not None:
        try:
            preview = json.dumps(first_evt, indent=2)[:1500]
        except Exception:
            preview = repr(first_evt)[:1500]
        sys.stderr.write(
            "[parallel] zero parsed — first /result shape diagnostic:\n"
            f"  top-level keys: {list(first_evt.keys()) if isinstance(first_evt, dict) else 'n/a'}\n"
            f"  raw (truncated to 1500 chars):\n{preview}\n"
        )

    append_master(new_rows)
    sys.stdout.write(f"[extract] appended {len(new_rows)} rows to {MASTER_CSV.relative_to(REPO_ROOT)}\n")

    # Quick signal-score histogram (threshold = SIGNAL_SCORE_LOAD_THRESHOLD)
    buckets = {f"<{SIGNAL_SCORE_LOAD_THRESHOLD} (park)": 0, f"{SIGNAL_SCORE_LOAD_THRESHOLD}-49": 0, "50-69": 0, "70+": 0}
    for r in new_rows:
        s = int(r["signal_score"]) if str(r["signal_score"]).isdigit() else 0
        if s < SIGNAL_SCORE_LOAD_THRESHOLD:
            key = f"<{SIGNAL_SCORE_LOAD_THRESHOLD} (park)"
        elif s < 50:
            key = f"{SIGNAL_SCORE_LOAD_THRESHOLD}-49"
        elif s < 70:
            key = "50-69"
        else:
            key = "70+"
        buckets[key] += 1
    sys.stdout.write("[extract] signal-score buckets: " + ", ".join(f"{k}={v}" for k, v in buckets.items()) + "\n")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--run", help="Run directory timestamp, e.g. 20260501T181152Z")
    g.add_argument("--latest", action="store_true", help="Use the most recent run dir")
    p.add_argument(
        "--processor",
        default="base",
        choices=["base", "core", "pro", "ultra"],
        help="Parallel.ai processor tier (cost/quality ladder). base = cheapest.",
    )
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    run_dir: Optional[Path]
    if args.latest:
        run_dir = latest_run_dir()
        if run_dir is None:
            sys.stderr.write(f"No run dirs found under {RUNS_DIR}\n")
            return 2
    else:
        run_dir = RUNS_DIR / args.run
        if not run_dir.exists():
            sys.stderr.write(f"Run dir not found: {run_dir}\n")
            return 2

    return run(run_dir, args.processor, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
