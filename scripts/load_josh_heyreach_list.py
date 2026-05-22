#!/usr/bin/env python3
"""Load fixtures/josh_drs_group_2026/heyreach_import.csv into a HeyReach lead list.

Uses HeyReach public API (same auth as scripts/heyreach_accepts_pull.py).
Creates list if --list-id not provided.

Usage:
  python3 scripts/load_josh_heyreach_list.py --list-id 686808
  python3 scripts/load_josh_heyreach_list.py --create-list "Josh Drs Group Pilot 2026-05-22"
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
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env.local"
BASE = "https://api.heyreach.io/api/public"
IMPORT_CSV = REPO_ROOT / "fixtures" / "josh_drs_group_2026" / "heyreach_import.csv"
BATCH_SIZE = 100


def load_env_local() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def api_post(path: str, body: dict) -> dict:
    key = os.environ.get("HEYREACH_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Missing HEYREACH_API_KEY in .env.local")
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "X-API-KEY": key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} {path}: {err_body[:500]}") from e
    if not raw:
        return {}
    return json.loads(raw)


def create_list(name: str) -> int:
    data = api_post(
        "/list/CreateEmptyList",
        {"listName": name, "listType": "USER_LIST"},
    )
    lid = data.get("id") or data.get("listId")
    if not lid:
        raise RuntimeError(f"CreateEmptyList unexpected response: {data}")
    return int(lid)


def lead_from_row(row: dict[str, str]) -> dict:
    notes = (row.get("notes") or "")[:500]
    fields = []
    for name, key in [
        ("persona", "persona"),
        ("subtier", "subtier_code"),
        ("message_lane", "message_lane"),
        ("signal", "signal"),
    ]:
        v = (row.get(key) or "").strip()
        if v:
            fields.append({"name": name, "value": v[:200]})
    return {
        "profileUrl": (row.get("profileUrl") or "").strip(),
        "firstName": (row.get("firstName") or "").strip() or None,
        "lastName": (row.get("lastName") or "").strip() or None,
        "companyName": (row.get("companyName") or "").strip() or None,
        "position": ((row.get("position") or "").strip()[:200] or None),
        "summary": notes or None,
        "customUserFields": fields or None,
    }


def add_leads(list_id: int, leads: list[dict]) -> dict:
    return api_post(
        "/list/AddLeadsToListV2",
        {"listId": list_id, "leads": leads},
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--list-id", type=int, default=686808)
    p.add_argument("--create-list", type=str, default="")
    p.add_argument("--csv", type=Path, default=IMPORT_CSV)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    load_env_local()

    if not args.csv.exists():
        sys.stderr.write(f"Missing {args.csv}\n")
        return 2

    rows = list(csv.DictReader(args.csv.open(encoding="utf-8-sig")))
    leads = [lead_from_row(r) for r in rows if (r.get("profileUrl") or "").strip()]
    if not leads:
        sys.stderr.write("No leads with profileUrl\n")
        return 2

    list_id = args.list_id
    if args.create_list:
        if args.dry_run:
            sys.stdout.write(f"Would create list: {args.create_list}\n")
        else:
            list_id = create_list(args.create_list)
            sys.stdout.write(f"Created list id={list_id}\n")

    sys.stdout.write(f"Loading {len(leads)} leads into list {list_id}…\n")

    totals = {"added": 0, "updated": 0, "failed": 0}
    for i in range(0, len(leads), BATCH_SIZE):
        chunk = leads[i : i + BATCH_SIZE]
        if args.dry_run:
            sys.stdout.write(f"  dry-run batch {i // BATCH_SIZE + 1}: {len(chunk)} leads\n")
            continue
        result = add_leads(list_id, chunk)
        totals["added"] += int(
            result.get("addedLeadsCount")
            or result.get("addedCount")
            or result.get("added")
            or 0
        )
        totals["updated"] += int(
            result.get("updatedLeadsCount")
            or result.get("updatedCount")
            or result.get("updated")
            or 0
        )
        totals["failed"] += int(
            result.get("failedLeadsCount")
            or result.get("failedCount")
            or result.get("failed")
            or 0
        )
        sys.stdout.write(f"  batch {i // BATCH_SIZE + 1}: {result}\n")
        time.sleep(0.3)

    sys.stdout.write(f"Done. listId={list_id} totals={totals}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
