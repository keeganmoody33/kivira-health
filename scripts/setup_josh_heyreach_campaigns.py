#!/usr/bin/env python3
"""Create Josh pilot HeyReach lists + cluster campaigns, load leads, resume.

Uses POST /list/CreateEmptyList, POST /campaign/Create, AddLeadsToCampaignV2, Resume.
"""

from __future__ import annotations

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
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

CLUSTER_META = {
    "A": ("Josh-Pilot-ClusterA-Provider-20260522", "Josh-Pilot-List-A-20260522"),
    "B": ("Josh-Pilot-ClusterB-VBC-20260522", "Josh-Pilot-List-B-20260522"),
    "C": ("Josh-Pilot-ClusterC-CareMgmt-20260522", "Josh-Pilot-List-C-20260522"),
    "D": ("Josh-Pilot-ClusterD-Partnership-20260522", "Josh-Pilot-List-D-20260522"),
    "E": ("Josh-Pilot-ClusterE-Founder-20260522", "Josh-Pilot-List-E-20260522"),
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


def lead_from_row(row: dict[str, str]) -> dict:
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
        "profileUrl": (row.get("profileUrl") or "").strip(),
        "firstName": (row.get("firstName") or "").strip() or None,
        "lastName": (row.get("lastName") or "").strip() or None,
        "companyName": (row.get("companyName") or "").strip() or None,
        "position": ((row.get("position") or "").strip()[:200] or None),
        "summary": ((row.get("notes") or "")[:500] or None),
        "customUserFields": fields or None,
    }


def bucket_rows() -> dict[str, list[dict[str, str]]]:
    buckets = {c: [] for c in CLUSTER_META}
    seen: set[str] = set()
    for row in csv.DictReader(IMPORT_CSV.open(encoding="utf-8-sig")):
        url = (row.get("profileUrl") or "").strip().lower()
        if not url or url in seen:
            continue
        seen.add(url)
        title = (row.get("position") or "").strip()
        cluster, _ = classify_first_touch_cluster(
            title,
            persona=(row.get("persona") or ""),
            subtier=(row.get("subtier_code") or row.get("subtier") or ""),
            company=(row.get("companyName") or ""),
            headline=title,
            about=(row.get("notes") or ""),
        )
        row = dict(row)
        row["_cluster"] = cluster
        buckets[cluster].append(row)
    return buckets


def create_list(name: str) -> int:
    data = api_post("/list/CreateEmptyList", {"listName": name, "listType": "USER_LIST"})
    lid = data.get("id") or data.get("listId")
    if not lid:
        raise RuntimeError(f"CreateEmptyList failed: {data}")
    return int(lid)


def add_leads_to_list(list_id: int, leads: list[dict]) -> None:
    for i in range(0, len(leads), BATCH):
        chunk = leads[i : i + BATCH]
        api_post("/list/AddLeadsToListV2", {"listId": list_id, "leads": chunk})
        time.sleep(0.3)


def create_campaign(name: str, list_id: int) -> int:
    data = api_post(
        "/campaign/Create",
        {
            "name": name,
            "LinkedInAccountIds": [LINKEDIN_ACCOUNT],
            "linkedInUserListId": list_id,
        },
    )
    cid = data.get("campaignId")
    if not cid:
        raise RuntimeError(f"Create failed: {data}")
    return int(cid)


def add_leads_to_campaign(campaign_id: int, leads: list[dict]) -> dict:
    totals = {"added": 0, "failed": 0}
    for i in range(0, len(leads), BATCH):
        chunk = leads[i : i + BATCH]
        pairs = [{"linkedInAccountId": LINKEDIN_ACCOUNT, "lead": ld} for ld in chunk]
        r = api_post(
            "/campaign/AddLeadsToCampaignV2",
            {"campaignId": campaign_id, "accountLeadPairs": pairs},
        )
        totals["added"] += int(r.get("addedLeadsCount") or 0)
        totals["failed"] += int(r.get("failedLeadsCount") or 0)
        time.sleep(0.35)
    return totals


def resume_campaign(campaign_id: int) -> None:
    api_post("/campaign/Resume", {"campaignId": campaign_id})


def main() -> int:
    load_env()
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    buckets = bucket_rows()
    result: dict[str, dict] = {}

    for cluster, (camp_name, list_name) in CLUSTER_META.items():
        rows = buckets[cluster]
        leads = [lead_from_row(r) for r in rows]
        print(f"\n=== Cluster {cluster}: {len(leads)} leads ===")

        existing_cid = cfg.get(cluster)
        if existing_cid and cluster == "A":
            cid = int(existing_cid)
            print(f"  Reuse campaign {cid}")
        else:
            list_id = create_list(list_name)
            print(f"  List {list_name} id={list_id}")
            if leads:
                add_leads_to_list(list_id, leads)
            cid = create_campaign(camp_name, list_id)
            print(f"  Campaign {camp_name} id={cid}")

        if leads:
            totals = add_leads_to_campaign(cid, leads)
            print(f"  Campaign load: {totals}")

        try:
            resume_campaign(cid)
            print(f"  Resumed campaign {cid}")
        except RuntimeError as e:
            print(f"  Resume skipped: {e}")

        result[cluster] = {
            "campaign_id": cid,
            "campaign_name": camp_name,
            "lead_count": len(leads),
        }
        cfg[cluster] = cid

    cfg["go_live_approved"] = True
    cfg["setup_completed"] = "2026-05-22"
    cfg["cluster_campaigns"] = result
    CONFIG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    print("\nWrote", CONFIG)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
