#!/usr/bin/env python3
"""Pre-run credit/balance check for all Kivira pipeline tools.

Run this before any Spider or Parallel job to confirm funds and key validity.
Prints a clear status block — green means go, warnings mean investigate first.

Usage:
    python3 scripts/check_credits.py

Checks:
    Spider   — exact credit balance via GET /data/credits
               ⚠️  flags failed_payment if present
    Parallel — key validity ping (no public balance endpoint exists;
               check https://platform.parallel.ai for dollar balance)
    HeyReach — key validity ping via GET /v1/lists

Reads keys from .env.local (same as all other scripts in this repo).
"""

from __future__ import annotations

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_env() -> None:
    env_path = REPO_ROOT / ".env.local"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def _get(url: str, headers: dict, timeout: int = 8) -> tuple[int, dict | str]:
    """GET url, return (status_code, parsed_json_or_text)."""
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8")
            try:
                return r.status, json.loads(body)
            except json.JSONDecodeError:
                return r.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, body


def _post(url: str, headers: dict, body: dict, timeout: int = 8) -> tuple[int, dict | str]:
    """POST url with JSON body, return (status_code, parsed_json_or_text)."""
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            resp_body = r.read().decode("utf-8")
            try:
                return r.status, json.loads(resp_body)
            except json.JSONDecodeError:
                return r.status, resp_body
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(resp_body)
        except json.JSONDecodeError:
            return e.code, resp_body


def check_spider(key: str) -> None:
    print("── Spider ─────────────────────────────────────────────")
    if not key:
        print("  ✗  SPIDER_API_KEY not set in .env.local")
        return

    status, data = _get(
        "https://api.spider.cloud/data/credits",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    if status == 200 and isinstance(data, dict):
        info = data.get("data", {})
        credits = float(info.get("credits", 0))
        failed = info.get("failed_payment")
        print(f"  Credits:  {credits:,.0f}")
        if credits < 10_000:
            print(f"  ⚠️  LOW — consider reloading before a full run")
        else:
            print(f"  ✓  Sufficient for current pipeline")
        if failed:
            print(f"  ⚠️  Failed payment on {failed} — resolve at spider.cloud/billing")
        else:
            print(f"  ✓  No payment issues")
    elif status == 401:
        print("  ✗  Invalid key (401)")
    else:
        print(f"  ?  Unexpected response {status}: {str(data)[:100]}")


def check_parallel(key: str) -> None:
    print("── Parallel ───────────────────────────────────────────")
    if not key:
        print("  ✗  PARALLEL_API_KEY not set in .env.local")
        return

    # No public balance endpoint — ping the task groups URL (GET → 405 = auth OK)
    status, data = _get(
        "https://api.parallel.ai/v1beta/tasks/groups",
        headers={"x-api-key": key, "Accept": "application/json"},
    )
    if status == 405:
        # Method Not Allowed = endpoint exists, auth succeeded
        print("  ✓  Key valid (auth confirmed)")
    elif status in (200, 201):
        print("  ✓  Key valid")
    elif status == 401:
        print("  ✗  Invalid key (401)")
    elif status == 402:
        print("  ✗  Insufficient credits (402) — reload at platform.parallel.ai")
    else:
        print(f"  ?  Status {status} — may still be valid")

    # Parallel has no programmatic balance endpoint
    print("  ℹ️  Balance: check https://platform.parallel.ai/billing")
    print("       (no public /credits API endpoint — dashboard only)")


def check_heyreach(key: str) -> None:
    print("── HeyReach ───────────────────────────────────────────")
    if not key:
        print("  ✗  HEYREACH_API_KEY not set in .env.local")
        return

    # Correct endpoint: POST /list/GetAll (no version prefix in base URL)
    # Confirmed from heyreach-cli source: github.com/bcharleson/heyreach-cli
    status, data = _post(
        "https://api.heyreach.io/api/public/list/GetAll",
        headers={
            "X-API-KEY": key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        body={"offset": 0, "limit": 5},
    )
    if status == 200 and isinstance(data, dict):
        total = data.get("totalCount", "?")
        print(f"  ✓  Key valid — {total} list(s) in account")
    elif status == 200:
        print("  ✓  Key valid")
    elif status == 401:
        print("  ✗  Invalid key (401)")
    elif status == 403:
        print("  ✗  Forbidden (403) — check key permissions")
    else:
        print(f"  ?  Status {status}: {str(data)[:100]}")
    print("  ℹ️  Usage/limits: check https://app.heyreach.io")


def main() -> int:
    load_env()

    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║           Kivira Pipeline — Credit Check             ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()

    check_spider(os.environ.get("SPIDER_API_KEY", ""))
    print()
    check_parallel(os.environ.get("PARALLEL_API_KEY", ""))
    print()
    check_heyreach(os.environ.get("HEYREACH_API_KEY", ""))
    print()
    print("───────────────────────────────────────────────────────")
    print("Run this before any Spider or Parallel job.")
    print("Spider threshold: 10,000 credits (~1,000 searches at optimized params)")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
