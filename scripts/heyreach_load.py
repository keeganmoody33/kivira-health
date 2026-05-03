#!/usr/bin/env python3
"""HeyReach API loader — push wave1_heyreach_ready.csv into active campaigns.

Reads the export from `scripts/export_heyreach_leads.py`, splits by persona,
and POSTs to `https://api.heyreach.io/api/public/campaign/AddLeadsToCampaignV2`
in batches.

Persona → campaign ID mapping is loaded from
`fixtures/wave1_campaign_ids.json` if present, otherwise the built-in defaults
below (verified via campaign/GetAll on 2026-05-03).

Campaigns must be ACTIVE (`IN_PROGRESS`) with LinkedIn senders attached for
lead-add to schedule connection requests automatically. HeyReach paces at the
account's daily cap (~25/day on free LinkedIn).

Usage:
  python3 scripts/heyreach_load.py                         # dry run (default)
  python3 scripts/heyreach_load.py --commit                # actually POST
  python3 scripts/heyreach_load.py --commit --max-per-campaign 25
  python3 scripts/heyreach_load.py --in fixtures/wave1_heyreach_ready.csv
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
DEFAULT_INPUT = REPO_ROOT / "fixtures" / "wave1_heyreach_ready.csv"
DEFAULT_CAMPAIGN_IDS = REPO_ROOT / "fixtures" / "wave1_campaign_ids.json"

HEYREACH_BASE = "https://api.heyreach.io/api/public"
ADD_LEADS_URL = f"{HEYREACH_BASE}/campaign/AddLeadsToCampaignV2"
GET_CAMPAIGNS_URL = f"{HEYREACH_BASE}/campaign/GetAll"

# Built-in defaults (verified 2026-05-03 against the user's HeyReach workspace).
# Override via fixtures/wave1_campaign_ids.json.
DEFAULT_PERSONA_TO_CAMPAIGN = {
    "operational_owner": 416316,    # Wave1-OperationalOwner (IN_PROGRESS)
    "clinical_champion": 416299,    # Wave1-ClinicalChampion (IN_PROGRESS)
    # No active campaigns yet for these personas — leads of these types get held.
    # "economic_buyer": ...
    # "tech_gatekeeper": ...
    # "bh_quality_influencer": ...
}

BATCH_SIZE = 100  # HeyReach AddLeadsV2 caps at 100 leads per call


def load_env_local() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"'))


def heyreach_post(url: str, body: dict, api_key: str) -> tuple[int, dict | str]:
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
        with urllib.request.urlopen(req, timeout=30) as resp:
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


def load_campaign_id_map() -> dict[str, int]:
    if DEFAULT_CAMPAIGN_IDS.exists():
        try:
            data = json.loads(DEFAULT_CAMPAIGN_IDS.read_text(encoding="utf-8"))
            return {k: int(v) for k, v in data.items() if v}
        except Exception:
            pass
    return dict(DEFAULT_PERSONA_TO_CAMPAIGN)


def lead_dict_from_row(row: dict[str, str]) -> dict[str, str]:
    """Build a HeyReach-shaped lead dict from a wave1_heyreach_ready row."""
    return {
        "profileUrl": (row.get("profileUrl") or "").strip(),
        "firstName": (row.get("firstName") or "").strip(),
        "lastName": (row.get("lastName") or "").strip(),
        "companyName": (row.get("companyName") or "").strip(),
        "position": (row.get("position") or "").strip(),
    }


def confirm_campaigns_active(api_key: str, campaign_ids: list[int]) -> dict[int, str]:
    """Return {campaign_id: status} for the requested IDs. Skips IDs not found."""
    status, body = heyreach_post(GET_CAMPAIGNS_URL, {"pageNumber": 0, "pageSize": 100}, api_key)
    out: dict[int, str] = {}
    if status != 200 or not isinstance(body, dict):
        return out
    items = body.get("items") or body.get("data") or []
    for c in items:
        cid = c.get("id")
        if cid in campaign_ids:
            out[cid] = c.get("status", "?")
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--in", dest="input_csv", default=str(DEFAULT_INPUT))
    p.add_argument("--commit", action="store_true", help="Actually POST. Default is dry run.")
    p.add_argument(
        "--max-per-campaign",
        type=int,
        default=25,
        help="Cap leads per campaign per run (matches HeyReach free-LinkedIn 25/day).",
    )
    args = p.parse_args(argv)

    load_env_local()
    api_key = os.environ.get("HEYREACH_API_KEY", "")
    if not api_key:
        print("ERROR: HEYREACH_API_KEY missing from .env.local", file=sys.stderr)
        return 2

    in_path = Path(args.input_csv)
    if not in_path.exists():
        print(f"ERROR: input not found: {in_path}", file=sys.stderr)
        return 2

    persona_to_campaign = load_campaign_id_map()
    print(f"Persona → campaign map: {persona_to_campaign}", file=sys.stderr)

    with in_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"Loaded {len(rows)} leads from {in_path.name}", file=sys.stderr)

    # Bucket by persona
    buckets: dict[str, list[dict]] = {}
    skipped_no_campaign = 0
    for r in rows:
        persona = (r.get("persona") or "").strip()
        if persona not in persona_to_campaign:
            skipped_no_campaign += 1
            continue
        buckets.setdefault(persona, []).append(r)

    if skipped_no_campaign:
        print(
            f"NOTE: {skipped_no_campaign} leads skipped — persona has no active campaign mapping",
            file=sys.stderr,
        )

    # Verify campaigns are reachable
    campaign_ids = list(persona_to_campaign.values())
    campaign_status = confirm_campaigns_active(api_key, campaign_ids)
    print(f"Campaign status: {campaign_status}", file=sys.stderr)
    for cid in campaign_ids:
        if cid not in campaign_status:
            print(f"  WARNING: campaign {cid} not reachable via API — leads may fail", file=sys.stderr)

    # Build per-campaign payloads, capped at --max-per-campaign
    plan: list[tuple[int, str, list[dict]]] = []
    for persona, persona_rows in buckets.items():
        cid = persona_to_campaign[persona]
        capped = persona_rows[: args.max_per_campaign]
        plan.append((cid, persona, capped))
        print(
            f"  {persona} → campaign {cid}: {len(capped)} of {len(persona_rows)} (cap {args.max_per_campaign})",
            file=sys.stderr,
        )

    if not args.commit:
        print("\nDRY RUN — pass --commit to actually POST these to HeyReach.", file=sys.stderr)
        for cid, persona, capped in plan:
            print(f"\n[Would POST] campaign={cid} persona={persona}")
            for r in capped[:3]:
                print(f"  {r['firstName']} {r['lastName']} — {r['position']} @ {r['companyName']}")
            if len(capped) > 3:
                print(f"  ... and {len(capped) - 3} more")
        return 0

    # Actually load
    total_added = 0
    total_failed = 0
    for cid, persona, capped in plan:
        for i in range(0, len(capped), BATCH_SIZE):
            batch = capped[i : i + BATCH_SIZE]
            payload = {
                "campaignId": cid,
                "AccountLeadPairs": [{"lead": lead_dict_from_row(r)} for r in batch],
            }
            print(
                f"POST {persona} → campaign {cid} (batch {i // BATCH_SIZE + 1}, "
                f"{len(batch)} leads)...",
                file=sys.stderr,
            )
            status, body = heyreach_post(ADD_LEADS_URL, payload, api_key)
            if status == 200 and isinstance(body, dict):
                added = body.get("addedLeadsCount", 0)
                updated = body.get("updatedLeadsCount", 0)
                failed = body.get("failedLeadsCount", 0)
                print(
                    f"  added={added}, updated={updated}, failed={failed}",
                    file=sys.stderr,
                )
                total_added += added
                total_failed += failed
            else:
                print(f"  HTTP {status}: {body}", file=sys.stderr)
                total_failed += len(batch)
            time.sleep(0.4)  # gentle rate-limit

    print(
        f"\nDONE — total added={total_added}, total failed={total_failed}",
        file=sys.stderr,
    )
    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
