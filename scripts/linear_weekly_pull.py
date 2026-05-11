#!/usr/bin/env python3
"""Linear weekly evidence puller — shipped + in-progress + backlog for the LEC team.

Pulls live Linear GraphQL data and prints the metric tables that feed the
weekly evidence node at `knowledge_base/execution/linear/weekly-shipped-YYYY-MM-DD.md`.

Mirrors the HeyReach REST puller pattern (`scripts/heyreach_weekly_pull.py`)
so the Friday ritual works the same way for both surfaces — one command, one
markdown blob ready to drop into the evidence node.

Endpoints:
  POST https://api.linear.app/graphql with Authorization: <api-key> header

Queries:
  - viewer + teams (sanity)
  - team(id).issues filtered by completedAt >= since (shipped)
  - team(id).issues filtered by createdAt >= since (created this week)
  - team(id).issues filtered by state.type = "started" (in progress)
  - team(id).issues filtered by state.type IN ("unstarted","backlog") (backlog)

Usage:
  python3 scripts/linear_weekly_pull.py                      # last 7 days
  python3 scripts/linear_weekly_pull.py --since 2026-05-04
  python3 scripts/linear_weekly_pull.py --json
  python3 scripts/linear_weekly_pull.py --team RGL           # different team

Reads LINEAR_API_KEY from `.env.local` (same convention as heyreach_load.py).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = REPO_ROOT / ".env.local"

API_URL = "https://api.linear.app/graphql"

# LEC = the GTM / Trial & Terror team. Verified against /viewer query on 2026-05-11.
DEFAULT_TEAM_KEY = "LEC"


def load_env_local() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def gql(query: str, variables: dict | None = None, timeout: int = 30) -> dict:
    body = json.dumps({"query": query, "variables": variables or {}}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": os.environ["LINEAR_API_KEY"],
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Linear API error {e.code}: {e.read().decode('utf-8', errors='replace')[:300]}")
    if data.get("errors"):
        raise RuntimeError(f"Linear GraphQL errors: {data['errors']}")
    return data["data"]


def get_team_id(team_key: str) -> tuple[str, str]:
    """Return (id, name) for the given team key."""
    data = gql("{ teams(first: 25) { nodes { id key name } } }")
    for t in data["teams"]["nodes"]:
        if t["key"].upper() == team_key.upper():
            return t["id"], t["name"]
    raise RuntimeError(f"Team key '{team_key}' not found in workspace")


def issues_completed_since(team_id: str, since_iso: str) -> list[dict]:
    data = gql(
        """
        query Completed($teamId: String!, $since: DateTimeOrDuration!) {
          team(id: $teamId) {
            issues(filter: { completedAt: { gte: $since } }, orderBy: updatedAt, first: 100) {
              nodes { identifier title state { name type } completedAt createdAt }
            }
          }
        }
        """,
        {"teamId": team_id, "since": since_iso},
    )
    return data["team"]["issues"]["nodes"]


def issues_created_since(team_id: str, since_iso: str) -> list[dict]:
    data = gql(
        """
        query Created($teamId: String!, $since: DateTimeOrDuration!) {
          team(id: $teamId) {
            issues(filter: { createdAt: { gte: $since } }, orderBy: createdAt, first: 100) {
              nodes { identifier title state { name type } createdAt completedAt }
            }
          }
        }
        """,
        {"teamId": team_id, "since": since_iso},
    )
    return data["team"]["issues"]["nodes"]


def issues_by_state_type(team_id: str, state_types: list[str]) -> list[dict]:
    """Return open issues whose state.type is in the given list (started, unstarted, backlog, triage)."""
    # Linear doesn't support `IN` on the type filter directly; pull each type and merge.
    out: list[dict] = []
    seen: set[str] = set()
    for stype in state_types:
        data = gql(
            """
            query ByState($teamId: String!, $stype: String!) {
              team(id: $teamId) {
                issues(filter: { state: { type: { eq: $stype } } }, orderBy: updatedAt, first: 50) {
                  nodes { identifier title state { name type } updatedAt createdAt }
                }
              }
            }
            """,
            {"teamId": team_id, "stype": stype},
        )
        for n in data["team"]["issues"]["nodes"]:
            if n["identifier"] not in seen:
                out.append(n)
                seen.add(n["identifier"])
    return out


def render_text(team_key: str, team_name: str, since_iso: str,
                completed: list[dict], created: list[dict],
                in_progress: list[dict], backlog: list[dict]) -> str:
    lines = []
    lines.append(f"# Linear weekly pull — team {team_key} ({team_name})")
    lines.append(f"# Generated: {datetime.now(timezone.utc).isoformat()}  Since: {since_iso}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Shipped (completed >= cutoff) | {len(completed)} |")
    lines.append(f"| Created (createdAt >= cutoff) | {len(created)} |")
    lines.append(f"| Currently In Progress | {len(in_progress)} |")
    lines.append(f"| Backlog (top of list) | {len(backlog)} |")
    lines.append("")

    lines.append("## Shipped (Done) this period")
    lines.append("")
    if completed:
        lines.append("| Issue | Title | Completed |")
        lines.append("|-------|-------|-----------|")
        for n in completed:
            title = (n["title"][:75] + "…") if len(n["title"]) > 75 else n["title"]
            lines.append(f"| **{n['identifier']}** | {title} | {n.get('completedAt','-')[:10]} |")
    else:
        lines.append("_No issues shipped in this window._")
    lines.append("")

    lines.append("## Created this period")
    lines.append("")
    if created:
        lines.append("| Issue | Title | State |")
        lines.append("|-------|-------|-------|")
        for n in created:
            title = (n["title"][:75] + "…") if len(n["title"]) > 75 else n["title"]
            lines.append(f"| {n['identifier']} | {title} | {n['state']['name']} |")
    else:
        lines.append("_No issues created in this window._")
    lines.append("")

    lines.append("## Currently In Progress")
    lines.append("")
    if in_progress:
        for n in in_progress:
            lines.append(f"- **{n['identifier']}** — {n['title']}")
    else:
        lines.append("_None in progress._")
    lines.append("")

    lines.append("## Backlog (active items only)")
    lines.append("")
    if backlog:
        for n in backlog:
            lines.append(f"- {n['identifier']} ({n['state']['name']}) — {n['title']}")
    else:
        lines.append("_Empty._")
    return "\n".join(lines)


def render_json(team_key: str, team_name: str, since_iso: str,
                completed: list[dict], created: list[dict],
                in_progress: list[dict], backlog: list[dict]) -> str:
    return json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "team_key": team_key,
        "team_name": team_name,
        "since": since_iso,
        "shipped": completed,
        "created": created,
        "in_progress": in_progress,
        "backlog": backlog,
        "counts": {
            "shipped": len(completed),
            "created": len(created),
            "in_progress": len(in_progress),
            "backlog": len(backlog),
        },
    }, indent=2, default=str)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--team", default=DEFAULT_TEAM_KEY, help=f"Linear team key (default: {DEFAULT_TEAM_KEY})")
    default_since = (date.today() - timedelta(days=7)).isoformat()
    p.add_argument("--since", default=default_since, metavar="YYYY-MM-DD",
                   help=f"Cutoff for completed/created filters (default: {default_since}, =7 days ago)")
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = p.parse_args()

    load_env_local()
    if "LINEAR_API_KEY" not in os.environ:
        sys.stderr.write("LINEAR_API_KEY not set (check .env.local)\n")
        return 2

    try:
        d = date.fromisoformat(args.since)
        since_iso = f"{d.isoformat()}T00:00:00.000Z"
    except ValueError as e:
        sys.stderr.write(f"bad --since: {e}\n")
        return 2

    try:
        team_id, team_name = get_team_id(args.team)
        completed = issues_completed_since(team_id, since_iso)
        created = issues_created_since(team_id, since_iso)
        in_progress = issues_by_state_type(team_id, ["started"])
        backlog = issues_by_state_type(team_id, ["unstarted", "backlog"])
    except RuntimeError as e:
        sys.stderr.write(f"{e}\n")
        return 1

    if args.json:
        print(render_json(args.team, team_name, since_iso, completed, created, in_progress, backlog))
    else:
        print(render_text(args.team, team_name, since_iso, completed, created, in_progress, backlog))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
