#!/usr/bin/env python3
"""Wire Josh pilot leads into v6 first-touch cluster campaigns (A through E).

Uses KIVIRA_FIRST_TOUCH_LINKEDIN_PLAYBOOK cluster routing, not message_lane.

Prerequisites:
  1. List 686808 loaded (scripts/load_josh_heyreach_list.py)
  2. Five PAUSED campaigns in HeyReach UI with copy from heyreach_first_touch_v6_templates.md
  3. Campaign IDs in fixtures/josh_drs_group_2026/josh_campaign_ids.json

Usage:
  python3 scripts/wire_josh_heyreach_campaigns.py              # dry-run
  python3 scripts/wire_josh_heyreach_campaigns.py --commit   # add leads (stay paused)
  python3 scripts/wire_josh_heyreach_campaigns.py --go-live  # resume (needs go_live_approved)
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
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tam_builder.josh_pilot.first_touch_cluster import (  # noqa: E402
    classify_first_touch_cluster,
)

ENV_FILE = REPO_ROOT / ".env.local"
CONFIG = REPO_ROOT / "fixtures" / "josh_drs_group_2026" / "josh_campaign_ids.json"
IMPORT_CSV = REPO_ROOT / "fixtures" / "josh_drs_group_2026" / "heyreach_import.csv"
BASE = "https://api.heyreach.io/api/public"
CLUSTERS = ("A", "B", "C", "D", "E")
BATCH_SIZE = 100

CAMPAIGN_UI_NAMES = {
    "A": "Josh-Pilot-ClusterA-Provider-20260522",
    "B": "Josh-Pilot-ClusterB-VBC-20260522",
    "C": "Josh-Pilot-ClusterC-CareMgmt-20260522",
    "D": "Josh-Pilot-ClusterD-Partnership-20260522",
    "E": "Josh-Pilot-ClusterE-Founder-20260522",
}


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
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} {path}: {err[:500]}") from e
    return json.loads(raw) if raw else {}


def load_config() -> dict:
    if not CONFIG.exists():
        raise RuntimeError(f"Missing config: {CONFIG}")
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def lead_pair_from_row(row: dict[str, str], linkedin_account_id: int | None) -> dict:
    notes = (row.get("notes") or "")[:500]
    cluster = row.get("_cluster") or ""
    fields = []
    for name, key in [
        ("persona", "persona"),
        ("subtier", "subtier_code"),
        ("first_touch_cluster", "_cluster"),
        ("cluster_rationale", "_cluster_rationale"),
        ("signal", "signal"),
    ]:
        v = (row.get(key) or "").strip()
        if v:
            fields.append({"name": name, "value": v[:200]})
    lead = {
        "profileUrl": (row.get("profileUrl") or "").strip(),
        "firstName": (row.get("firstName") or "").strip() or None,
        "lastName": (row.get("lastName") or "").strip() or None,
        "companyName": (row.get("companyName") or "").strip() or None,
        "position": ((row.get("position") or "").strip()[:200] or None),
        "summary": notes or None,
        "customUserFields": fields or None,
    }
    pair: dict = {"lead": lead}
    if linkedin_account_id:
        pair["linkedInAccountId"] = linkedin_account_id
    return pair


def enrich_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        url = (row.get("profileUrl") or "").strip().lower()
        if not url or url in seen:
            continue
        seen.add(url)
        title = (row.get("position") or "").strip()
        cluster, rationale = classify_first_touch_cluster(
            title,
            persona=(row.get("persona") or ""),
            subtier=(row.get("subtier_code") or row.get("subtier") or ""),
            company=(row.get("companyName") or ""),
            headline=title,
            about=(row.get("notes") or ""),
        )
        row = dict(row)
        row["_cluster"] = cluster
        row["_cluster_rationale"] = rationale
        out.append(row)
    return out


def bucket_rows(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    buckets: dict[str, list[dict[str, str]]] = {c: [] for c in CLUSTERS}
    for row in rows:
        cluster = row.get("_cluster", "E")
        if cluster in buckets:
            buckets[cluster].append(row)
    return buckets


def get_campaign_status(campaign_id: int) -> str | None:
    data = api_post("/campaign/GetById", {"campaignId": campaign_id})
    return data.get("status") if isinstance(data, dict) else None


def add_leads_to_campaign(campaign_id: int, pairs: list[dict]) -> dict:
    totals = {"added": 0, "updated": 0, "failed": 0}
    for i in range(0, len(pairs), BATCH_SIZE):
        chunk = pairs[i : i + BATCH_SIZE]
        result = api_post(
            "/campaign/AddLeadsToCampaignV2",
            {"campaignId": campaign_id, "accountLeadPairs": chunk},
        )
        totals["added"] += int(result.get("addedLeadsCount") or 0)
        totals["updated"] += int(result.get("updatedLeadsCount") or 0)
        totals["failed"] += int(result.get("failedLeadsCount") or 0)
        print(f"    batch {i // BATCH_SIZE + 1}: {result}")
        time.sleep(0.35)
    return totals


def resume_campaign(campaign_id: int) -> None:
    api_post("/campaign/Resume", {"campaignId": campaign_id})


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--commit", action="store_true")
    p.add_argument("--go-live", action="store_true")
    p.add_argument("--csv", type=Path, default=IMPORT_CSV)
    args = p.parse_args()

    load_env_local()
    cfg = load_config()

    if not args.csv.exists():
        sys.stderr.write(f"Missing {args.csv}\n")
        return 2

    rows = enrich_rows(list(csv.DictReader(args.csv.open(encoding="utf-8-sig"))))
    buckets = bucket_rows(rows)

    cluster_ids = {c: cfg.get(c) for c in CLUSTERS}
    missing = [c for c in CLUSTERS if not cluster_ids.get(c)]
    linkedin_account_id = cfg.get("linkedin_account_id")
    approved = bool(cfg.get("go_live_approved"))

    print("Josh pilot — v6 cluster campaign wiring")
    print(f"  list: {cfg.get('list_name')} (id {cfg.get('list_id')})")
    print(f"  playbook: {cfg.get('playbook', 'KIVIRA_FIRST_TOUCH_LINKEDIN_PLAYBOOK')}")
    print(f"  go_live_approved: {approved}")
    print("  cluster counts:", {c: len(buckets[c]) for c in CLUSTERS})
    print("  campaign IDs:", cluster_ids)

    if args.go_live:
        if not approved:
            sys.stderr.write(
                "REFUSED: set go_live_approved: true in josh_campaign_ids.json after Keegan approves.\n"
            )
            return 2
        for c in CLUSTERS:
            cid = int(cluster_ids[c])
            print(f"Resuming cluster {c} campaign {cid} (was {get_campaign_status(cid)})…")
            resume_campaign(cid)
        print("Go-live: resume requested for clusters A through E.")
        return 0

    if missing:
        print("\nBLOCKED — create PAUSED campaigns in HeyReach UI, then paste IDs:")
        for c in missing:
            print(f"  {c}: null → {CAMPAIGN_UI_NAMES[c]}")
        print("\nTemplates: fixtures/josh_drs_group_2026/heyreach_first_touch_v6_templates.md")
        print("Checklist: fixtures/josh_drs_group_2026/GO_LIVE_CHECKLIST.md")
        if not args.commit:
            return 0
        return 2

    if not args.commit:
        print("\nDRY RUN — would add leads:")
        for c in CLUSTERS:
            print(f"  {c} → {CAMPAIGN_UI_NAMES[c]} (id {cluster_ids[c]}): {len(buckets[c])} leads")
        print("\nNext: --commit then approve → --go-live")
        return 0

    grand = {"added": 0, "updated": 0, "failed": 0}
    for c in CLUSTERS:
        cid = int(cluster_ids[c])
        pairs = [
            lead_pair_from_row(r, linkedin_account_id) for r in buckets[c]
        ]
        print(f"\nCluster {c} → campaign {cid} ({len(pairs)} leads)…")
        totals = add_leads_to_campaign(cid, pairs)
        for k in grand:
            grand[k] += totals[k]

    print(f"\nDone (campaigns still paused unless you --go-live). totals={grand}")
    return 0 if grand["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
