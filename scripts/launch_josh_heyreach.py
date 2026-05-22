#!/usr/bin/env python3
"""Launch Josh pilot on HeyReach via existing PAUSED campaigns (sequences already set).

API-created campaigns stay DRAFT until a sequence is saved in the HeyReach UI.
This script routes cluster leads into Wave1 PAUSED campaigns and resumes them.

Mapping (v6 cluster → campaign with live sequence):
  A, C → Wave1-OperationalOwner (416316)
  B    → Wave1-ClinicalChampion (416299)
  D, E → Wave1-Baseline-9Subtier (416629)

Usage:
  python3 scripts/launch_josh_heyreach.py           # dry-run
  python3 scripts/launch_josh_heyreach.py --commit  # load + resume
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
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tam_builder.josh_pilot.first_touch_cluster import classify_first_touch_cluster

ENV_FILE = REPO_ROOT / ".env.local"
CONFIG = REPO_ROOT / "fixtures" / "josh_drs_group_2026" / "josh_campaign_ids.json"
IMPORT_CSV = REPO_ROOT / "fixtures" / "josh_drs_group_2026" / "heyreach_import.csv"
BASE = "https://api.heyreach.io/api/public"
LINKEDIN_ACCOUNT = 192406
BATCH = 100

# Wave1 campaigns with configured sequences (PAUSED at last check).
CLUSTER_TO_CAMPAIGN = {
    "A": (416316, "Wave1-OperationalOwner"),
    "C": (416316, "Wave1-OperationalOwner"),
    "B": (416299, "Wave1-ClinicalChampion"),
    "D": (416629, "Wave1-Baseline-9Subtier-20260503"),
    "E": (416629, "Wave1-Baseline-9Subtier-20260503"),
}

# API-created DRAFT shells (need UI sequence before use).
DRAFT_CAMPAIGNS = {
    "combined_list_id": 686853,
    "combined_campaign_id": 441566,
    "cluster_a_draft_id": 441560,
}


def load_env() -> None:
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
        raise RuntimeError("Missing HEYREACH_API_KEY")
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode(),
        headers={
            "X-API-KEY": key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode()
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} {path}: {e.read().decode()[:500]}") from e
    return json.loads(raw) if raw else {}


def bucket_by_campaign() -> dict[int, list[dict[str, str]]]:
    buckets: dict[int, list[dict[str, str]]] = defaultdict(list)
    seen: set[str] = set()
    for row in csv.DictReader(IMPORT_CSV.open(encoding="utf-8-sig")):
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
        cid, _ = CLUSTER_TO_CAMPAIGN[cluster]
        row = dict(row)
        row["_cluster"] = cluster
        row["_cluster_rationale"] = rationale
        buckets[cid].append(row)
    return buckets


def lead_pair(row: dict[str, str]) -> dict:
    fields = []
    for name, key in [
        ("persona", "persona"),
        ("subtier", "subtier_code"),
        ("first_touch_cluster", "_cluster"),
        ("signal", "signal"),
    ]:
        v = (row.get(key) or "").strip()
        if v:
            fields.append({"name": name, "value": v[:200]})
    return {
        "linkedInAccountId": LINKEDIN_ACCOUNT,
        "lead": {
            "profileUrl": (row.get("profileUrl") or "").strip(),
            "firstName": (row.get("firstName") or "").strip() or None,
            "lastName": (row.get("lastName") or "").strip() or None,
            "companyName": (row.get("companyName") or "").strip() or None,
            "position": ((row.get("position") or "").strip()[:200] or None),
            "summary": ((row.get("notes") or "")[:500] or None),
            "customUserFields": fields or None,
        },
    }


def add_leads(campaign_id: int, rows: list[dict[str, str]]) -> dict:
    totals = {"added": 0, "updated": 0, "failed": 0}
    pairs = [lead_pair(r) for r in rows]
    for i in range(0, len(pairs), BATCH):
        chunk = pairs[i : i + BATCH]
        r = api_post(
            "/campaign/AddLeadsToCampaignV2",
            {"campaignId": campaign_id, "accountLeadPairs": chunk},
        )
        totals["added"] += int(r.get("addedLeadsCount") or 0)
        totals["updated"] += int(r.get("updatedLeadsCount") or 0)
        totals["failed"] += int(r.get("failedLeadsCount") or 0)
        print(f"    batch {i // BATCH + 1}: {r}")
        time.sleep(0.35)
    return totals


def resume(campaign_id: int) -> None:
    """REST Resume body casing is inconsistent; try MCP-equivalent paths."""
    for body in (
        {"campaignId": campaign_id},
        {"CampaignId": campaign_id},
        {"id": campaign_id},
    ):
        try:
            api_post("/campaign/Resume", body)
            return
        except RuntimeError:
            continue
    raise RuntimeError(
        f"Could not resume campaign {campaign_id} via API. "
        "Use HeyReach UI or MCP resume_campaign."
    )


def campaign_status(campaign_id: int) -> str:
    data = api_post("/campaign/GetAll", {"offset": 0, "limit": 100})
    for item in data.get("items") or []:
        if item.get("id") == campaign_id:
            return item.get("status", "?")
    return "?"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--commit", action="store_true")
    args = p.parse_args()

    load_env()
    buckets = bucket_by_campaign()

    print("Josh pilot launch plan (Wave1 PAUSED campaigns with sequences)")
    for cluster, (cid, name) in CLUSTER_TO_CAMPAIGN.items():
        print(f"  cluster {cluster} → {name} ({cid})")

    by_cid: dict[int, tuple[str, list]] = {}
    for cluster, (cid, name) in CLUSTER_TO_CAMPAIGN.items():
        if cid not in by_cid:
            by_cid[cid] = (name, [])
        by_cid[cid][1].extend(buckets.get(cid, []))

    for cid, (name, rows) in sorted(by_cid.items()):
        # dedupe per campaign bucket
        seen: set[str] = set()
        unique = []
        for r in rows:
            u = (r.get("profileUrl") or "").lower()
            if u not in seen:
                seen.add(u)
                unique.append(r)
        print(f"\nCampaign {cid} ({name}): {len(unique)} Josh leads, status={campaign_status(cid)}")

    if not args.commit:
        print("\nDRY RUN — pass --commit to load and resume.")
        return 0

    totals_all = {"added": 0, "failed": 0}
    resumed: list[int] = []
    for cid, (name, rows) in sorted(by_cid.items()):
        seen: set[str] = set()
        unique = []
        for r in rows:
            u = (r.get("profileUrl") or "").lower()
            if u not in seen:
                seen.add(u)
                unique.append(r)
        if not unique:
            continue
        print(f"\nLoading {len(unique)} into {name} ({cid})…")
        t = add_leads(cid, unique)
        totals_all["added"] += t["added"]
        totals_all["failed"] += t["failed"]
        st = campaign_status(cid)
        if st == "PAUSED":
            resume(cid)
            resumed.append(cid)
            print(f"  Resumed {cid}")
        else:
            print(f"  Skip resume (status={st})")

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    cfg["go_live_approved"] = True
    cfg["launch_mode"] = "wave1_paused_campaigns_with_sequences"
    cfg["launched_at"] = "2026-05-22"
    cfg["campaign_mapping"] = {
        "A": 416316,
        "B": 416299,
        "C": 416316,
        "D": 416629,
        "E": 416629,
    }
    cfg["draft_for_ui_sequence"] = DRAFT_CAMPAIGNS
    cfg["master_list_id"] = 686808
    CONFIG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")

    print(f"\nDone. added={totals_all['added']} failed={totals_all['failed']} resumed={resumed}")
    print("NOTE: LinkedIn sender 192406 was inactive in API; reconnect in HeyReach if sends stall.")
    print("NOTE: Paste v6 first-DM copy from heyreach_first_touch_v6_templates.md into draft campaign 441566 in UI for true v6 messaging.")
    return 0 if totals_all["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
