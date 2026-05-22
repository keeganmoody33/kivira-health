#!/usr/bin/env python3
"""HeyReach list-member puller — dumps every lead in one or more lists.

Unlike the campaign endpoints (which only expose aggregate progressStats), the
list endpoint returns full per-lead records, including the HeyReach-enriched
`imageUrl` (profile photo), `headline`, `connections`, and `followers`.

Endpoint:
  POST /list/GetLeadsFromList  {listId, offset, limit}  -> {items[], totalCount}

A campaign's backing list id is on the campaign object as `linkedInUserListId`
(POST /campaign/GetAll). Wave 1 mapping (verified 2026-05-22):
  416316 Wave1-OperationalOwner  -> list 646679 "Wave 1 — 2A ACO Named Contacts" (359)
  416299 Wave1-ClinicalChampion  -> list 646680 "Wave 1 — 1C Provider Group Personas" (590)

Usage:
  python3 scripts/heyreach_list_pull.py --list-ids 646679 646680 \
      --labels OperationalOwner ClinicalChampion \
      --out fixtures/heyreach_pending_2026-05-22/pending_raw.csv

Reads HEYREACH_API_KEY from .env.local.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env.local"
BASE = "https://api.heyreach.io/api/public"

CSV_FIELDS = [
    "list_id", "source_campaign", "profileUrl", "firstName", "lastName",
    "position", "headline", "companyName", "location",
    "imageUrl", "has_photo", "connections", "followers",
    "emailAddress", "about", "id", "linkedin_id",
]


def load_env_local() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def _post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "X-API-KEY": os.environ["HEYREACH_API_KEY"],
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def pull_list(list_id: int) -> list[dict]:
    out: list[dict] = []
    offset = 0
    while True:
        data = _post("/list/GetLeadsFromList", {"listId": list_id, "offset": offset, "limit": 100})
        items = data.get("items", []) or []
        out.extend(items)
        if len(items) < 100:
            break
        offset += 100
    return out


def to_row(lead: dict, list_id: int, label: str) -> dict:
    image = lead.get("imageUrl")
    return {
        "list_id": list_id,
        "source_campaign": label,
        "profileUrl": lead.get("profileUrl") or "",
        "firstName": lead.get("firstName") or "",
        "lastName": lead.get("lastName") or "",
        "position": lead.get("position") or "",
        "headline": (lead.get("headline") or "").replace("\n", " "),
        "companyName": lead.get("companyName") or "",
        "location": lead.get("location") or "",
        "imageUrl": image or "",
        "has_photo": "true" if image else "false",
        "connections": lead.get("connections", 0),
        "followers": lead.get("followers", 0),
        "emailAddress": lead.get("emailAddress") or lead.get("enrichedEmailAddress") or "",
        "about": (lead.get("about") or "").replace("\n", " ")[:400],
        "id": lead.get("id") or "",
        "linkedin_id": lead.get("linkedin_id") or "",
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--list-ids", nargs="+", type=int, required=True)
    p.add_argument("--labels", nargs="*", default=None,
                   help="Optional label per list-id (e.g. campaign name)")
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)

    labels = args.labels or [str(lid) for lid in args.list_ids]
    if len(labels) != len(args.list_ids):
        sys.stderr.write("--labels count must match --list-ids count\n")
        return 2

    load_env_local()
    if "HEYREACH_API_KEY" not in os.environ:
        sys.stderr.write("HEYREACH_API_KEY not set (check .env.local)\n")
        return 2

    rows: list[dict] = []
    for lid, label in zip(args.list_ids, labels):
        leads = pull_list(lid)
        sys.stderr.write(f"list {lid} ({label}): pulled {len(leads)} leads\n")
        rows.extend(to_row(l, lid, label) for l in leads)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(rows)
    sys.stderr.write(f"Wrote {len(rows)} rows -> {out}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
