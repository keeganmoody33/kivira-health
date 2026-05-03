#!/usr/bin/env python3
"""Create a new HeyReach lead list and load the randomized 270-lead batch.

API-doable workflow (the public API can't create a campaign with a list
attached, and won't add leads to a DRAFT campaign — so we do as much as
possible via API and leave a small UI step for the user):

1. Create an empty list via /list/CreateEmptyList → list_id
2. Add all leads via /list/AddLeadsToListV2 in batches of 100
3. Print a UI action checklist for the user

After the user creates the campaign in the HeyReach UI selecting this list,
HeyReach starts sending connection requests at the LinkedIn daily cap.

Usage:
  python3 scripts/heyreach_create_and_load_test.py            # dry run
  python3 scripts/heyreach_create_and_load_test.py --commit   # create list + load
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
DEFAULT_INPUT = REPO_ROOT / "fixtures" / "randomized_test_batch.csv"

HEYREACH_BASE = "https://api.heyreach.io/api/public"
CREATE_LIST_URL = f"{HEYREACH_BASE}/list/CreateEmptyList"
ADD_LEADS_TO_LIST_URL = f"{HEYREACH_BASE}/list/AddLeadsToListV2"

DEFAULT_LIST_NAME = "Wave1-Baseline-9Subtier-Leads-20260503"
DEFAULT_CAMPAIGN_NAME = "Wave1-Baseline-9Subtier-20260503"
BATCH_SIZE = 100


def load_env_local() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"'))


def heyreach_post(url: str, body: dict, api_key: str, timeout: int = 30) -> tuple[int, dict | str]:
    req = urllib.request.Request(
        url,
        method="POST",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(body_text)
        except json.JSONDecodeError:
            return e.code, body_text


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--in", dest="input_csv", default=str(DEFAULT_INPUT))
    p.add_argument("--list-name", default=DEFAULT_LIST_NAME)
    p.add_argument("--campaign-name", default=DEFAULT_CAMPAIGN_NAME)
    p.add_argument("--commit", action="store_true", help="Actually POST. Default is dry run.")
    args = p.parse_args(argv)

    load_env_local()
    api_key = os.environ.get("HEYREACH_API_KEY", "")
    if not api_key:
        print("ERROR: HEYREACH_API_KEY missing", file=sys.stderr)
        return 2

    in_path = Path(args.input_csv)
    if not in_path.exists():
        print(f"ERROR: input not found: {in_path}", file=sys.stderr)
        return 2

    with in_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"Loaded {len(rows)} leads from {in_path.name}", file=sys.stderr)

    if not args.commit:
        print(f"\nDRY RUN — would create list '{args.list_name}' and load {len(rows)} leads.", file=sys.stderr)
        print(f"  → {(len(rows) + BATCH_SIZE - 1) // BATCH_SIZE} batch(es) of {BATCH_SIZE}", file=sys.stderr)
        print("\nAfter list is loaded, you'll create the campaign in HeyReach UI:", file=sys.stderr)
        print(f"  Name: {args.campaign_name}", file=sys.stderr)
        print(f"  Sender: 192406 (Keegan)", file=sys.stderr)
        print(f"  Lead source: '{args.list_name}'", file=sys.stderr)
        print(f"  Sequence: connection request only, no personalized note", file=sys.stderr)
        return 0

    # 1. Create empty list
    print(f"\nCreating list '{args.list_name}'...", file=sys.stderr)
    status, body = heyreach_post(CREATE_LIST_URL, {"Name": args.list_name}, api_key)
    if status != 200 or not isinstance(body, dict):
        print(f"ERROR: list create failed: {status} {body}", file=sys.stderr)
        return 2
    list_id = body.get("id")
    if not list_id:
        print(f"ERROR: no list id in response: {body}", file=sys.stderr)
        return 2
    print(f"  Created list id={list_id}", file=sys.stderr)

    # 2. Add leads to list in batches
    total_added = 0
    total_failed = 0
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        payload = {
            "ListId": list_id,
            "Leads": [
                {
                    "profileUrl": (r.get("profileUrl") or "").strip(),
                    "firstName": (r.get("firstName") or "").strip(),
                    "lastName": (r.get("lastName") or "").strip(),
                    "companyName": (r.get("companyName") or "").strip(),
                    "position": (r.get("position") or "").strip(),
                }
                for r in batch
            ],
        }
        print(f"  POST batch {i // BATCH_SIZE + 1} ({len(batch)} leads)...", file=sys.stderr)
        status, body = heyreach_post(ADD_LEADS_TO_LIST_URL, payload, api_key)
        if status == 200 and isinstance(body, dict):
            added = body.get("addedLeadsCount", 0)
            updated = body.get("updatedLeadsCount", 0)
            failed = body.get("failedLeadsCount", 0)
            print(f"    added={added} updated={updated} failed={failed}", file=sys.stderr)
            total_added += added
            total_failed += failed
        else:
            print(f"    HTTP {status}: {body}", file=sys.stderr)
            total_failed += len(batch)
        time.sleep(0.5)

    print(
        f"\n=== List ready: '{args.list_name}' (id={list_id}) ===",
        file=sys.stderr,
    )
    print(f"  Total leads added: {total_added}", file=sys.stderr)
    print(f"  Failed: {total_failed}", file=sys.stderr)
    print("\n=== UI action needed (~30 seconds) ===", file=sys.stderr)
    print("  1. HeyReach UI → Campaigns → New Campaign", file=sys.stderr)
    print(f"  2. Name: {args.campaign_name}", file=sys.stderr)
    print(f"  3. LinkedIn sender: Keegan Moody (id 192406)", file=sys.stderr)
    print(f"  4. Lead source → My Lists → '{args.list_name}' (id {list_id})", file=sys.stderr)
    print("  5. Sequence: connection request only, NO personalized note", file=sys.stderr)
    print("  6. Daily limit: keep at LinkedIn cap (~25)", file=sys.stderr)
    print("  7. START the campaign", file=sys.stderr)
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
