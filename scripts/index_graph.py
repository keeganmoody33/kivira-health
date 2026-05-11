#!/usr/bin/env python3
"""
index_graph.py — Context OS fast-lookup index generator.

Scans all markdown knowledge nodes, extracts frontmatter, resolves
[[wiki-links]], builds a backlink index, checks taxonomy compliance,
and writes:

  _system/GRAPH_INDEX.md   — human-readable fast-lookup (primary artifact)
  _system/GRAPH_INDEX.json — machine-readable full index

Usage:
  python scripts/index_graph.py
  python scripts/index_graph.py --root /path/to/KIVIRA.HEALTH
  python scripts/index_graph.py --out-md _system/GRAPH_INDEX.md

Design intent:
  Every future session should start by reading GRAPH_INDEX.md to know:
    1. Where every node lives (Path Map — grep-able, one line per node)
    2. What links to a node (Backlink Index)
    3. Health status at a glance (Orphans, Taxonomy Issues, Tag Frequency)
  No more blind find/grep across the repo.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Scan targets
# ---------------------------------------------------------------------------

SCAN_DIRS = [
    "knowledge_base",
    "00_foundation",
    "_system/agent_workflows",
    ".claude/skills",
    "gtm-context-os-quickstart/.claude/skills",
]

SKIP_DIRS = {".venv", ".git", "__pycache__", ".pytest_cache", ".obsidian"}

# ---------------------------------------------------------------------------
# Wikilink parser
# ---------------------------------------------------------------------------
#
# Standard Obsidian wikilink syntax: [[name]] or [[name|display]]. Captures
# the first segment; display alias after `|` is consumed and discarded.
# Names that don't resolve against the node name_map are silently dropped.
# Per CLAUDE.md HARD RULE #8, v1 taxonomy.yaml / ontology.yaml are retired —
# v2 lets the corpus define its own categories via heat and inbound links.

WIKILINK_RE = re.compile(r"\[\[([^\]\\|]+?)(?:\\?\|[^\]]*)?\]\]")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Node:
    path: Path                        # absolute
    rel_path: str                     # relative to repo root
    name: str
    description: str
    domain: str
    node_type: str
    status: str
    last_updated: str
    tags: list[str]
    topics: list[str]
    related_concepts: list[str]       # raw [[FOO]] strings from frontmatter
    source_type: str
    source_file: str
    body_lines: int
    frontmatter_raw: str
    body_raw: str
    # populated after full scan:
    outbound: list[str] = field(default_factory=list)   # node names this links to
    inbound: list[str] = field(default_factory=list)    # node names that link here


@dataclass
class WorkflowEntry:
    rel_path: str
    name: str
    description: str


@dataclass
class SkillEntry:
    rel_path: str
    name: str
    description: str


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _extract_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_block, body). Empty strings if no frontmatter."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return "", text
    return m.group(1), text[m.end():]


def _parse_fm_field(fm: str, key: str) -> str:
    """Extract a scalar string field from raw YAML-like frontmatter."""
    pattern = re.compile(rf"^{re.escape(key)}:\s*(.+)$", re.MULTILINE)
    m = pattern.search(fm)
    if not m:
        return ""
    return m.group(1).strip().strip('"').strip("'")


def _parse_fm_list(fm: str, key: str) -> list[str]:
    """Extract a list field (indented `- item` entries) from frontmatter."""
    # Find the key line, then consume following `  - ` lines.
    lines = fm.splitlines()
    result: list[str] = []
    in_key = False
    for line in lines:
        if re.match(rf"^{re.escape(key)}\s*:", line):
            in_key = True
            continue
        if in_key:
            m = re.match(r"^\s+-\s+(.+)$", line)
            if m:
                result.append(m.group(1).strip().strip('"').strip("'"))
            elif line.strip() and not line.startswith(" "):
                break  # hit next top-level key
    return result


def _parse_fm_nested(fm: str, parent_key: str, child_key: str) -> str:
    """Extract source.type / source.file style nested scalar."""
    lines = fm.splitlines()
    in_parent = False
    for line in lines:
        if re.match(rf"^{re.escape(parent_key)}\s*:", line):
            in_parent = True
            continue
        if in_parent:
            m = re.match(rf"^\s+{re.escape(child_key)}\s*:\s*(.+)$", line)
            if m:
                return m.group(1).strip().strip('"').strip("'")
            if line.strip() and not line.startswith(" "):
                break
    return ""


def _extract_wikilinks(text: str) -> list[str]:
    return list(dict.fromkeys(WIKILINK_RE.findall(text)))  # deduplicated, order-preserving


def _first_heading_or_filename(path: Path, body: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def _parse_skill_description(text: str) -> str:
    """Best-effort: grab first non-empty line after any frontmatter."""
    _, body = _extract_frontmatter(text)
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped[:120]
    return ""


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def scan_repo(root: Path) -> tuple[list[Node], list[WorkflowEntry], list[SkillEntry]]:
    nodes: list[Node] = []
    workflows: list[WorkflowEntry] = []
    skills: list[SkillEntry] = []

    for scan_dir_name in SCAN_DIRS:
        scan_dir = root / scan_dir_name
        if not scan_dir.exists():
            continue

        for md_path in sorted(scan_dir.rglob("*.md")):
            # Skip any hidden/venv subdirs
            if any(part in SKIP_DIRS for part in md_path.parts):
                continue

            text = md_path.read_text(encoding="utf-8", errors="replace")
            fm_raw, body = _extract_frontmatter(text)
            rel = md_path.relative_to(root).as_posix()

            # Workflows
            if "_system/agent_workflows" in rel:
                name = _parse_fm_field(fm_raw, "name") or md_path.stem
                desc = _parse_fm_field(fm_raw, "description") or _parse_skill_description(body)
                workflows.append(WorkflowEntry(rel_path=rel, name=name, description=desc[:120]))
                continue

            # Skills (SKILL.md files)
            if md_path.name == "SKILL.md":
                name = _parse_fm_field(fm_raw, "name") or md_path.parent.name
                desc = _parse_fm_field(fm_raw, "description") or _parse_skill_description(body)
                skills.append(SkillEntry(rel_path=rel, name=name or md_path.parent.name, description=desc[:120]))
                continue

            # Knowledge / foundation nodes — require frontmatter with 'name'
            name = _parse_fm_field(fm_raw, "name")
            if not name:
                # Foundation synthesis docs may have no frontmatter — index lightly
                name = md_path.stem
                if not fm_raw:
                    nodes.append(Node(
                        path=md_path, rel_path=rel, name=name,
                        description=_parse_skill_description(body)[:120],
                        domain="", node_type="", status="", last_updated="",
                        tags=[], topics=[], related_concepts=[],
                        source_type="", source_file="",
                        body_lines=len(body.splitlines()),
                        frontmatter_raw="", body_raw=body,
                    ))
                    continue

            node = Node(
                path=md_path,
                rel_path=rel,
                name=name,
                description=_parse_fm_field(fm_raw, "description"),
                domain=_parse_fm_field(fm_raw, "domain"),
                node_type=_parse_fm_field(fm_raw, "node_type"),
                status=_parse_fm_field(fm_raw, "status"),
                last_updated=_parse_fm_field(fm_raw, "last_updated"),
                tags=_parse_fm_list(fm_raw, "tags"),
                topics=_parse_fm_list(fm_raw, "topics"),
                related_concepts=_parse_fm_list(fm_raw, "related_concepts"),
                source_type=_parse_fm_nested(fm_raw, "source", "type"),
                source_file=_parse_fm_nested(fm_raw, "source", "file"),
                body_lines=len(body.splitlines()),
                frontmatter_raw=fm_raw,
                body_raw=body,
            )
            nodes.append(node)

    return nodes, workflows, skills


# ---------------------------------------------------------------------------
# Graph resolution
# ---------------------------------------------------------------------------

def resolve_links(nodes: list[Node]) -> None:
    """Populate outbound / inbound on every node by resolving [[wikilinks]]."""
    name_map: dict[str, Node] = {n.name: n for n in nodes}

    for node in nodes:
        # Links from frontmatter related_concepts + body
        fm_links = _extract_wikilinks(node.frontmatter_raw)
        body_links = _extract_wikilinks(node.body_raw)
        all_links = list(dict.fromkeys(fm_links + body_links))

        for target_name in all_links:
            if target_name == node.name:
                continue
            node.outbound.append(target_name)
            if target_name in name_map:
                name_map[target_name].inbound.append(node.name)


# ---------------------------------------------------------------------------
# Render markdown index
# ---------------------------------------------------------------------------

def _status_badge(status: str) -> str:
    return {"validated": "✅", "canonical": "⭐", "emergent": "🌱"}.get(status, "❓")


def render_index(
    nodes: list[Node],
    workflows: list[WorkflowEntry],
    skills: list[SkillEntry],
    root: Path,
    generated_at: str,
) -> str:
    lines: list[str] = []

    # Sort: validated first, then emergent, then canonical, alphabetical within
    STATUS_ORDER = {"canonical": 0, "validated": 1, "emergent": 2, "": 3}
    sorted_nodes = sorted(nodes, key=lambda n: (STATUS_ORDER.get(n.status, 9), n.domain, n.name))

    # Group for domain counts
    domain_counts: dict[str, int] = defaultdict(int)
    for n in nodes:
        domain_counts[n.domain or "unknown"] += 1

    total_links = sum(len(n.outbound) for n in nodes)
    orphans = [n for n in nodes if not n.inbound and n.domain]  # only real nodes
    low_outbound = [
        n for n in nodes
        if "knowledge_base" in n.rel_path and len(n.outbound) < 3
    ]

    # Tag frequency
    tag_freq: dict[str, int] = defaultdict(int)
    for n in nodes:
        for t in n.tags:
            tag_freq[t] += 1

    # ── Header ──────────────────────────────────────────────────────────────
    lines += [
        "# Context OS — Graph Index",
        f"> Generated: {generated_at}  |  Run `python scripts/index_graph.py` to refresh.",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total nodes indexed | {len(nodes)} |",
        f"| knowledge_base nodes | {sum(1 for n in nodes if 'knowledge_base' in n.rel_path)} |",
        f"| foundation / synthesis docs | {sum(1 for n in nodes if '00_foundation' in n.rel_path)} |",
        f"| Agent workflows | {len(workflows)} |",
        f"| Skills | {len(skills)} |",
        f"| Total wiki-links mapped | {total_links} |",
        f"| Orphan nodes (0 inbound) | {len(orphans)} |",
        f"| knowledge_base nodes with <3 outbound | {len(low_outbound)} |",
        "",
        "**Domains:**",
    ]
    for domain, count in sorted(domain_counts.items()):
        lines.append(f"- `{domain}`: {count} nodes")
    lines.append("")

    # ── Path Map ─────────────────────────────────────────────────────────────
    lines += [
        "---",
        "## Path Map",
        "",
        "> One line per node. `grep NODE_NAME _system/GRAPH_INDEX.md` finds path + status instantly.",
        "",
    ]
    max_name = max((len(n.name) for n in sorted_nodes), default=20)
    for n in sorted_nodes:
        badge = _status_badge(n.status)
        inb = len(n.inbound)
        lines.append(
            f"`{n.name:<{max_name}}` → `{n.rel_path}` {badge} [{n.domain}/{n.node_type}] ←{inb}"
        )
    lines.append("")

    # ── Node Registry (table) ────────────────────────────────────────────────
    lines += [
        "---",
        "## Node Registry",
        "",
        "| Node | Domain | Type | Status | ←Links | Lines | Description |",
        "|------|--------|------|--------|--------|-------|-------------|",
    ]
    for n in sorted_nodes:
        badge = _status_badge(n.status)
        desc = (n.description[:70] + "…") if len(n.description) > 70 else n.description
        lines.append(
            f"| `{n.name}` | {n.domain} | {n.node_type} | {badge} {n.status}"
            f" | {len(n.inbound)} | {n.body_lines} | {desc} |"
        )
    lines.append("")

    # ── Backlink Index ────────────────────────────────────────────────────────
    lines += [
        "---",
        "## Backlink Index",
        "",
        "> For each node: what links TO it (inbound) and what it links TO (outbound).",
        "",
    ]
    for n in sorted_nodes:
        if not n.inbound and not n.outbound:
            continue
        lines.append(f"### `{n.name}`")
        if n.inbound:
            lines.append(f"**←** {', '.join(f'`{x}`' for x in sorted(n.inbound))}")
        else:
            lines.append("**←** _(no inbound links — orphan)_")
        if n.outbound:
            lines.append(f"**→** {', '.join(f'`{x}`' for x in sorted(n.outbound))}")
        lines.append("")

    # ── Orphans ────────────────────────────────────────────────────────────────
    lines += [
        "---",
        "## Orphans (0 inbound links)",
        "",
    ]
    if orphans:
        lines.append("These nodes are never referenced by any other node — integration risk.")
        lines.append("")
        for n in orphans:
            lines.append(f"- `{n.name}` (`{n.rel_path}`) — {n.status} / {n.domain}")
    else:
        lines.append("_None. All nodes have at least one inbound link._ ✅")
    lines.append("")

    # ── Low Outbound (informational) ────────────────────────────────────────────
    lines += [
        "---",
        "## knowledge_base Nodes with <3 Outbound Links (informational)",
        "",
        "> Per Context OS v2, this is *not* an issue — atoms can have few outbound",
        "> connections when newly created. Listed here as a signal for follow-up",
        "> linking, not a blocker.",
        "",
    ]
    if low_outbound:
        for n in sorted(low_outbound, key=lambda x: (len(x.outbound), x.name)):
            lines.append(
                f"- `{n.name}` (`{n.rel_path}`) — {len(n.outbound)} outbound, {n.status}"
            )
    else:
        lines.append("_All knowledge_base nodes have ≥3 outbound links._ ✅")
    lines.append("")

    # ── Tag Frequency ───────────────────────────────────────────────────────────
    lines += [
        "---",
        "## Tag Frequency",
        "",
        "| Tag | Count |",
        "|-----|-------|",
    ]
    for tag, count in sorted(tag_freq.items(), key=lambda x: -x[1]):
        lines.append(f"| `{tag}` | {count} |")
    lines.append("")

    # ── Agent Workflows ──────────────────────────────────────────────────────────
    lines += [
        "---",
        "## Agent Workflows",
        "",
        "| Workflow | Path | Description |",
        "|----------|------|-------------|",
    ]
    for w in sorted(workflows, key=lambda x: x.name):
        desc = (w.description[:80] + "…") if len(w.description) > 80 else w.description
        lines.append(f"| `{w.name}` | `{w.rel_path}` | {desc} |")
    lines.append("")

    # ── Skills ──────────────────────────────────────────────────────────────────
    lines += [
        "---",
        "## Skills",
        "",
        "| Skill | Path | Description |",
        "|-------|------|-------------|",
    ]
    for s in sorted(skills, key=lambda x: x.name):
        desc = (s.description[:80] + "…") if len(s.description) > 80 else s.description
        lines.append(f"| `{s.name}` | `{s.rel_path}` | {desc} |")
    lines.append("")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Render JSON
# ---------------------------------------------------------------------------

def render_json(
    nodes: list[Node],
    workflows: list[WorkflowEntry],
    skills: list[SkillEntry],
    generated_at: str,
) -> str:
    def node_to_dict(n: Node) -> dict[str, Any]:
        return {
            "name": n.name,
            "rel_path": n.rel_path,
            "domain": n.domain,
            "node_type": n.node_type,
            "status": n.status,
            "last_updated": n.last_updated,
            "description": n.description,
            "tags": n.tags,
            "topics": n.topics,
            "related_concepts": n.related_concepts,
            "source_type": n.source_type,
            "source_file": n.source_file,
            "body_lines": n.body_lines,
            "outbound": n.outbound,
            "inbound": n.inbound,
        }

    data = {
        "generated_at": generated_at,
        "nodes": [node_to_dict(n) for n in nodes],
        "workflows": [{"name": w.name, "rel_path": w.rel_path, "description": w.description} for w in workflows],
        "skills": [{"name": s.name, "rel_path": s.rel_path, "description": s.description} for s in skills],
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Generate Context OS graph index.")
    p.add_argument("--root", default=".", help="Repo root (default: cwd)")
    p.add_argument("--out-md", default="_system/GRAPH_INDEX.md")
    p.add_argument("--out-json", default="_system/GRAPH_INDEX.json")
    p.add_argument("--no-json", action="store_true", help="Skip JSON output")
    args = p.parse_args(argv)

    root = Path(args.root).resolve()
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    print(f"Scanning {root} …", file=sys.stderr)
    nodes, workflows, skills = scan_repo(root)
    print(f"  Found {len(nodes)} nodes, {len(workflows)} workflows, {len(skills)} skills", file=sys.stderr)

    resolve_links(nodes)

    orphan_count = sum(1 for n in nodes if not n.inbound and n.domain)
    total_links = sum(len(n.outbound) for n in nodes)
    print(f"  {total_links} links resolved, {orphan_count} orphans", file=sys.stderr)

    md_path = root / args.out_md
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_index(nodes, workflows, skills, root, generated_at), encoding="utf-8")
    print(f"  ✓ {md_path.relative_to(root)}", file=sys.stderr)

    if not args.no_json:
        json_path = root / args.out_json
        json_path.write_text(render_json(nodes, workflows, skills, generated_at), encoding="utf-8")
        print(f"  ✓ {json_path.relative_to(root)}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
