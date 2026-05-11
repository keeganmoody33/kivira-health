#!/usr/bin/env python3
"""HeyReach accepts puller — one-shot CSV of all LinkedIn accepts with lead metadata.

Pulls every conversation (= every accept) from /inbox/GetConversationsV2 and
emits per-lead rows with the fields needed for sub-tier triage and follow-up.

This is a single-deliverable puller for the Josh follow-up package
(2026-05-11). For the recurring weekly evidence pull, see
`scripts/heyreach_weekly_pull.py`.

Output columns (CSV):
  first_name, last_name, position, headline, company, location,
  linkedin_url, source_campaign, accepted_at, replied,
  last_message_at, last_message_text

Notes:
  - HeyReach AI autoTagger only runs on conversations that get a reply, so
    `source_campaign` is populated for repliers and "—" for accept-only rows.
  - `accepted_at` is approximated as the createdAt of the first "ME" message
    in the thread — HeyReach fires the welcome message immediately after the
    LinkedIn accept, so the gap is seconds.

Usage:
  python3 scripts/heyreach_accepts_pull.py                # CSV to stdout
  python3 scripts/heyreach_accepts_pull.py --out file.csv # CSV to file
  python3 scripts/heyreach_accepts_pull.py --json         # JSON to stdout
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env.local"
BASE = "https://api.heyreach.io/api/public"


def load_env_local() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def _post(path: str, body: dict) -> dict:
    headers = {
        "X-API-KEY": os.environ["HEYREACH_API_KEY"],
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode("utf-8"),
        headers=headers, method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def get_all_conversations() -> list[dict]:
    out: list[dict] = []
    offset = 0
    while True:
        data = _post("/inbox/GetConversationsV2", {"offset": offset, "limit": 100})
        items = data.get("items", []) or []
        out.extend(items)
        if len(items) < 100:
            break
        offset += 100
    return out


def first_me_message_at(conv: dict) -> str:
    for m in conv.get("messages", []) or []:
        if m.get("sender") == "ME":
            return m.get("createdAt", "") or ""
    return ""


def source_campaign_from_autotags(conv: dict) -> str:
    tags = (conv.get("correspondentProfile") or {}).get("autoTags") or []
    names = [t.get("campaignName") for t in tags if t.get("campaignName")]
    return " | ".join(names) if names else "—"


def conv_to_row(conv: dict) -> dict:
    cp = conv.get("correspondentProfile") or {}
    return {
        "first_name": cp.get("firstName") or "",
        "last_name": cp.get("lastName") or "",
        "position": cp.get("position") or "",
        "headline": cp.get("headline") or "",
        "company": cp.get("companyName") or "",
        "location": cp.get("location") or "",
        "linkedin_url": cp.get("profileUrl") or "",
        "source_campaign": source_campaign_from_autotags(conv),
        "accepted_at": first_me_message_at(conv),
        "replied": conv.get("totalMessages", 0) > 1,
        "last_message_at": conv.get("lastMessageAt") or "",
        "last_message_text": (conv.get("lastMessageText") or "").replace("\n", " ")[:240],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default=None, help="Write CSV to this path (default: stdout)")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of CSV")
    args = p.parse_args()

    load_env_local()
    if "HEYREACH_API_KEY" not in os.environ:
        sys.stderr.write("HEYREACH_API_KEY not set (check .env.local)\n")
        return 2

    convs = get_all_conversations()
    rows = [conv_to_row(c) for c in convs]
    rows.sort(key=lambda r: r.get("accepted_at") or r.get("last_message_at") or "", reverse=True)

    sys.stderr.write(f"Pulled {len(rows)} accepts.\n")

    if args.json:
        print(json.dumps(rows, indent=2, default=str))
        return 0

    cols = ["first_name", "last_name", "position", "headline", "company",
            "location", "linkedin_url", "source_campaign", "accepted_at",
            "replied", "last_message_at", "last_message_text"]

    sink = open(args.out, "w", newline="", encoding="utf-8") if args.out else io.StringIO()
    w = csv.DictWriter(sink, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow(r)

    if args.out:
        sink.close()
        sys.stderr.write(f"Wrote {args.out}\n")
    else:
        print(sink.getvalue(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
