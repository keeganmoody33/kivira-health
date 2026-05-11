#!/usr/bin/env python3
"""HeyReach weekly evidence puller — campaign progress + inbox reply slice.

Pulls live HeyReach REST data and prints the metric tables that feed the
weekly evidence node at `knowledge_base/gtm_signals/heyreach/weekly-evidence-YYYY-MM-DD.md`.

Why this script: HeyReach MCP is wired in `.cursor/mcp.json` for Cursor, but
not in Claude Code or in CI. This script is the REST equivalent so the Friday
ritual works from any agent or CLI.

Endpoints:
  POST /campaign/GetAll                   — per-campaign progressStats (works)
  POST /inbox/GetConversationsV2          — conversations (filter args silently
                                            ignored; always returns workspace-wide,
                                            so we slice by date client-side)
  POST /li_account/GetAll                 — confirms sender count + identity

Usage:
  python3 scripts/heyreach_weekly_pull.py
  python3 scripts/heyreach_weekly_pull.py --since 2026-05-02
  python3 scripts/heyreach_weekly_pull.py --markdown        # emit evidence-node body
  python3 scripts/heyreach_weekly_pull.py --json            # machine-readable
  python3 scripts/heyreach_weekly_pull.py --campaign-ids 416316 416299

Reads HEYREACH_API_KEY from `.env.local` (same convention as `heyreach_load.py`).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env.local"

BASE = "https://api.heyreach.io/api/public"

# Wave 1 campaign IDs verified against /campaign/GetAll on 2026-05-10
DEFAULT_CAMPAIGN_IDS = [416629, 416316, 416299]


def load_env_local() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def _request(method: str, path: str, body: dict | None = None, timeout: int = 30) -> tuple[int, object]:
    headers = {
        "X-API-KEY": os.environ["HEYREACH_API_KEY"],
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw


def get_campaigns() -> dict[int, dict]:
    status, data = _request("POST", "/campaign/GetAll", {"offset": 0, "limit": 100})
    if status != 200 or not isinstance(data, dict):
        raise RuntimeError(f"/campaign/GetAll failed: {status} {str(data)[:200]}")
    return {c["id"]: c for c in data.get("items", [])}


def get_all_conversations() -> list[dict]:
    """Paginate /inbox/GetConversationsV2. Filter args are silently ignored, so
    we always pull workspace-wide and slice client-side."""
    out: list[dict] = []
    offset = 0
    while True:
        status, data = _request(
            "POST", "/inbox/GetConversationsV2", {"offset": offset, "limit": 100}
        )
        if status != 200 or not isinstance(data, dict):
            sys.stderr.write(f"GetConversationsV2 failed at offset={offset}: {status}\n")
            break
        items = data.get("items", [])
        out.extend(items)
        if len(items) < 100:
            break
        offset += 100
    return out


def get_senders() -> list[dict]:
    status, data = _request("POST", "/li_account/GetAll", {"offset": 0, "limit": 50})
    if status != 200 or not isinstance(data, dict):
        return []
    return data.get("items", [])


def metrics_from(convs: list[dict], cutoff_iso: str | None) -> dict:
    def is_post(c: dict) -> bool:
        if not cutoff_iso:
            return True
        return (c.get("lastMessageAt") or "") >= cutoff_iso

    post = [c for c in convs if is_post(c)]
    return {
        "total": len(convs),
        "post_launch_total": len(post),
        "correspondent_last": sum(1 for c in convs if c.get("lastMessageSender") == "CORRESPONDENT"),
        "post_correspondent_last": sum(1 for c in post if c.get("lastMessageSender") == "CORRESPONDENT"),
        "multi_message": sum(1 for c in convs if c.get("totalMessages", 0) > 1),
        "post_multi_message": sum(1 for c in post if c.get("totalMessages", 0) > 1),
        "unread_replies": sum(
            1 for c in convs if c.get("read") is False and c.get("lastMessageSender") == "CORRESPONDENT"
        ),
        "post_unread_replies": sum(
            1 for c in post if c.get("read") is False and c.get("lastMessageSender") == "CORRESPONDENT"
        ),
    }


def autotag_breakdown(convs: list[dict]) -> tuple[Counter, Counter, int]:
    """Return (campaign_attribution_counter, tag_name_counter, untagged_count)."""
    tag_camps: Counter = Counter()
    tag_names: Counter = Counter()
    untagged = 0
    for c in convs:
        tags = (c.get("correspondentProfile") or {}).get("autoTags") or []
        if not tags:
            untagged += 1
            continue
        for t in tags:
            tag_camps[(t.get("campaignId"), t.get("campaignName"))] += 1
            tag_names[t.get("name", "?")] += 1
    return tag_camps, tag_names, untagged


def render_text(
    campaigns: dict[int, dict],
    convs: list[dict],
    senders: list[dict],
    campaign_ids: list[int],
    cutoff_iso: str | None,
) -> str:
    out: list[str] = []
    out.append(f"# HeyReach weekly pull — {datetime.now(timezone.utc).isoformat()}")
    out.append(f"# Cutoff (post-launch slice): {cutoff_iso or 'none'}")
    out.append(f"# Senders attached: {len(senders)}  →  {[s.get('emailAddress') for s in senders]}")
    out.append("")

    out.append("## Campaign Progress")
    out.append("")
    out.append("| Campaign | Status | Loaded | InFlight | Pending | Finished | Failed | ExcludeInOther |")
    out.append("|----------|--------|--------|----------|---------|----------|--------|----------------|")
    tot = {"loaded": 0, "inflight": 0, "pending": 0, "finished": 0, "failed": 0}
    for cid in campaign_ids:
        c = campaigns.get(cid)
        if not c:
            out.append(f"| (id={cid} not found) | — | — | — | — | — | — | — |")
            continue
        ps = c.get("progressStats") or {}
        loaded = ps.get("totalUsers", 0)
        inflight = ps.get("totalUsersInProgress", 0)
        pending = ps.get("totalUsersPending", 0)
        finished = ps.get("totalUsersFinished", 0)
        failed = ps.get("totalUsersFailed", 0)
        tot["loaded"] += loaded
        tot["inflight"] += inflight
        tot["pending"] += pending
        tot["finished"] += finished
        tot["failed"] += failed
        excl = c.get("excludeInOtherCampaigns")
        out.append(
            f"| {c.get('name')} | {c.get('status')} | {loaded} | {inflight} | {pending} | "
            f"{finished} | {failed} | {excl} |"
        )
    out.append(
        f"| **TOTAL** | — | **{tot['loaded']}** | **{tot['inflight']}** | **{tot['pending']}** | "
        f"**{tot['finished']}** | **{tot['failed']}** | — |"
    )
    out.append("")

    m = metrics_from(convs, cutoff_iso)
    out.append("## Inbox (workspace-wide; per-campaign filter is broken upstream)")
    out.append("")
    out.append("| Metric | All-time | Post-launch |")
    out.append("|--------|----------|-------------|")
    out.append(f"| Conversations (= accepts) | {m['total']} | {m['post_launch_total']} |")
    out.append(f"| Replies (correspondent-last) | {m['correspondent_last']} | {m['post_correspondent_last']} |")
    out.append(f"| Multi-message threads | {m['multi_message']} | {m['post_multi_message']} |")
    out.append(f"| **Unread w/ reply (action needed)** | **{m['unread_replies']}** | **{m['post_unread_replies']}** |")
    out.append("")

    tag_camps, tag_names, untagged = autotag_breakdown(convs)
    out.append("## AutoTag Attribution (HeyReach AI tagger)")
    out.append("")
    if tag_camps:
        for (cid, cname), n in tag_camps.most_common():
            out.append(f"- {n}  → campaign {cid} ({cname})")
    out.append(f"- {untagged}  → no autoTag (manual or pre-tagger conversation)")
    out.append(f"- Tag names: {dict(tag_names) or '(none)'}")
    out.append("")

    out.append(f"## Recent Replies (post-launch, correspondent-last, top 20)")
    out.append("")
    replies = sorted(
        [c for c in convs if (cutoff_iso is None or (c.get("lastMessageAt") or "") >= cutoff_iso)
                          and c.get("lastMessageSender") == "CORRESPONDENT"],
        key=lambda c: c.get("lastMessageAt", ""), reverse=True,
    )
    if not replies:
        out.append("_(none)_")
    for r in replies[:20]:
        cp = r.get("correspondentProfile", {}) or {}
        name = f"{cp.get('firstName','')} {cp.get('lastName','')}".strip() or "?"
        when = r.get("lastMessageAt", "?")
        url = cp.get("profileUrl", "?")
        body = (r.get("lastMessageText") or "").replace("\n", " ")[:160]
        unread = "•" if r.get("read") is False else " "
        out.append(f"- {unread} `{when}` — **{name}** — {url}")
        out.append(f"    > {body}")
    return "\n".join(out)


def render_json(
    campaigns: dict[int, dict],
    convs: list[dict],
    senders: list[dict],
    campaign_ids: list[int],
    cutoff_iso: str | None,
) -> str:
    by_campaign = []
    for cid in campaign_ids:
        c = campaigns.get(cid, {})
        ps = c.get("progressStats") or {}
        by_campaign.append({
            "id": cid,
            "name": c.get("name"),
            "status": c.get("status"),
            "started_at": c.get("startedAt"),
            "exclude_in_other_campaigns": c.get("excludeInOtherCampaigns"),
            "loaded": ps.get("totalUsers", 0),
            "in_flight": ps.get("totalUsersInProgress", 0),
            "pending": ps.get("totalUsersPending", 0),
            "finished": ps.get("totalUsersFinished", 0),
            "failed": ps.get("totalUsersFailed", 0),
        })
    m = metrics_from(convs, cutoff_iso)
    tag_camps, tag_names, untagged = autotag_breakdown(convs)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "cutoff_iso": cutoff_iso,
        "sender_count": len(senders),
        "senders": [{"id": s.get("id"), "email": s.get("emailAddress")} for s in senders],
        "campaigns": by_campaign,
        "inbox_metrics": m,
        "autotag_attribution": [
            {"campaign_id": cid, "campaign_name": cname, "count": n}
            for (cid, cname), n in tag_camps.most_common()
        ],
        "autotag_untagged": untagged,
        "autotag_names": dict(tag_names),
    }
    return json.dumps(payload, indent=2)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--campaign-ids", nargs="*", type=int, default=DEFAULT_CAMPAIGN_IDS,
                   help=f"Campaign IDs to include (default: {DEFAULT_CAMPAIGN_IDS})")
    p.add_argument("--since", default=None, metavar="YYYY-MM-DD",
                   help="Post-launch cutoff for slicing inbox (e.g. 2026-05-02)")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of text")
    p.add_argument("--markdown", action="store_true", help="Emit markdown suitable for the evidence node body")
    args = p.parse_args()

    load_env_local()
    if "HEYREACH_API_KEY" not in os.environ:
        sys.stderr.write("HEYREACH_API_KEY not set (check .env.local)\n")
        return 2

    cutoff_iso = None
    if args.since:
        try:
            d = date.fromisoformat(args.since)
            cutoff_iso = f"{d.isoformat()}T00:00:00Z"
        except ValueError as e:
            sys.stderr.write(f"bad --since: {e}\n")
            return 2

    try:
        campaigns = get_campaigns()
        convs = get_all_conversations()
        senders = get_senders()
    except RuntimeError as e:
        sys.stderr.write(f"{e}\n")
        return 1

    if args.json:
        print(render_json(campaigns, convs, senders, args.campaign_ids, cutoff_iso))
    else:
        # --markdown is currently the same as the default text output (already markdown tables).
        # Kept as an explicit flag so callers can opt-in semantically.
        print(render_text(campaigns, convs, senders, args.campaign_ids, cutoff_iso))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
