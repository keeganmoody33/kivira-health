#!/usr/bin/env python3
"""Fetch results for an already-submitted Parallel.ai task group and append to
`fixtures/wave1_linkedin_master.csv`.

Use this when `parallel_persona_extractor.py` was killed/timed out mid-poll
(e.g., sandboxed bash terminating a detached process). The task group has
already been billed; this resumes only the result-fetching half of the
pipeline.

The mapping from `run_id` -> seed row is reconstructed by listing the task
group's runs via SSE (which Parallel returns ordered by `created_at`
ascending = submission order) and zipping against `collect_urls(run_dir)`,
which reads `Q*_raw_urls.json` deterministically (sorted glob).

Usage:
    python3 scripts/fetch_taskgroup_results.py \
        --taskgroup-id tgrp_fdd6b37846aa47afb0492bf91d08d9c0 \
        --run-dir 20260501T190409Z

Required env: PARALLEL_API_KEY (loaded from .env.local).
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Reuse helpers from the main extractor so logic stays identical.
from scripts.parallel_persona_extractor import (  # noqa: E402
    PARALLEL_RUN_RESULT,
    PARALLEL_TASK_GROUPS,
    PARALLEL_TIMEOUT_SECONDS,
    RUNS_DIR,
    _extract_content,
    _get_json,
    append_master,
    build_master_row,
    collect_urls,
    load_env_local,
)


def list_run_ids_in_submission_order(taskgroup_id: str, api_key: str) -> list[str]:
    """List run_ids in the taskgroup, ordered by submission (created_at asc).

    Parallel returns this as Server-Sent Events at
    GET /v1beta/tasks/groups/{tg_id}/runs. We parse the `data:` lines.
    """
    url = f"{PARALLEL_TASK_GROUPS}/{taskgroup_id}/runs"
    req = urllib.request.Request(
        url,
        headers={
            "x-api-key": api_key,
            "Accept": "text/event-stream",
        },
    )
    run_ids: list[str] = []
    with urllib.request.urlopen(req, timeout=PARALLEL_TIMEOUT_SECONDS) as resp:
        for raw in resp:
            line = raw.decode("utf-8", errors="replace").rstrip("\n")
            if not line.startswith("data:"):
                continue
            payload_str = line[len("data:"):].strip()
            if not payload_str:
                continue
            try:
                evt = json.loads(payload_str)
            except json.JSONDecodeError:
                continue
            run = evt.get("run") or {}
            rid = run.get("run_id")
            if rid:
                run_ids.append(rid)
    return run_ids


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--taskgroup-id", required=True)
    p.add_argument(
        "--run-dir",
        required=True,
        help="Run dir name under fixtures/wave1_runs (e.g. 20260501T190409Z)",
    )
    args = p.parse_args()

    load_env_local()
    import os

    api_key = os.environ.get("PARALLEL_API_KEY", "").strip()
    if not api_key:
        sys.stderr.write("Missing PARALLEL_API_KEY (set in .env.local)\n")
        return 2

    run_dir = RUNS_DIR / args.run_dir
    if not run_dir.exists():
        sys.stderr.write(f"Run dir not found: {run_dir}\n")
        return 1

    seeds = collect_urls(run_dir)
    sys.stdout.write(f"[fetch] {len(seeds)} seed URLs from {run_dir.name}\n")

    run_ids = list_run_ids_in_submission_order(args.taskgroup_id, api_key)
    sys.stdout.write(f"[fetch] {len(run_ids)} run_ids from taskgroup\n")

    if len(run_ids) != len(seeds):
        sys.stderr.write(
            f"[fetch] WARNING: run_id count ({len(run_ids)}) != seed count "
            f"({len(seeds)}). Zipping by min length — some rows may be misaligned.\n"
        )

    today = datetime.now(timezone.utc).date().isoformat()
    new_rows: list[dict] = []
    fetched = 0
    parsed = 0
    drop_reason_counts: dict[str, int] = {}
    first_evt = None

    for run_id, seed in zip(run_ids, seeds):
        url = f"{PARALLEL_RUN_RESULT}/{run_id}/result"
        try:
            evt = _get_json(url, api_key)
        except urllib.error.HTTPError as e:
            sys.stderr.write(
                f"[warn] HTTP {e.code} fetching run {run_id}: "
                f"{e.read().decode('utf-8', errors='replace')[:200]}\n"
            )
            continue
        except Exception as e:
            sys.stderr.write(f"[warn] failed to fetch run {run_id}: {e}\n")
            continue

        fetched += 1
        if first_evt is None:
            first_evt = evt

        content, drop_reason = _extract_content(evt)
        if drop_reason or content is None:
            key = drop_reason or "no-content"
            drop_reason_counts[key] = drop_reason_counts.get(key, 0) + 1
            continue

        new_rows.append(build_master_row(seed, content, today))
        parsed += 1

    sys.stdout.write(f"[fetch] fetched={fetched}  parsed={parsed}\n")
    if drop_reason_counts:
        sys.stdout.write(f"[fetch] drop reasons: {drop_reason_counts}\n")

    if fetched > 0 and parsed == 0 and first_evt is not None:
        try:
            preview = json.dumps(first_evt, indent=2)[:1500]
        except Exception:
            preview = repr(first_evt)[:1500]
        sys.stderr.write(
            "[fetch] zero parsed — first /result shape diagnostic:\n"
            + preview + "\n"
        )

    if new_rows:
        append_master(new_rows)
        sys.stdout.write(f"[fetch] appended {len(new_rows)} rows to master CSV\n")
    else:
        sys.stdout.write("[fetch] no rows to append\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
