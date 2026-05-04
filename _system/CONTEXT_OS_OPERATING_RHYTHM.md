# Context OS Operating Rhythm v2 (Kivira)

**Purpose:** Weekly MOC-driven loop. The graph compounds via use, not ceremony.
**Replaces:** `_system/CONTEXT_OS_OPERATING_RHYTHM.md` (v1 monthly ritual)

---

## Core Principle (v2)

> Desire paths are stigmergy. Agents coordinate by reading and modifying the shared environment — not by following procedures. If a file has zero heat, it's the concrete path nobody walks. Pave the desire paths. — Jacob Dielte, Context-OS v2

---

## The Weekly Loop: Friday Morning (45 min)

### SENSE (10 min)

1. Open Obsidian. Graph view: orange clusters = this week's activity.
2. Terminal: `context-os query heat --time 7d --limit 15`
3. Dataview: "Show me validated nodes with heat > 2"
4. Linear export: paste issues closed/created into chat

### ORIENT (10 min)

1. Click through hot nodes. Read frontmatter. Hover-preview linked nodes.
2. Identify complete signal chains: Search node → Capture node → Validate node, all linked.
3. Flag infrastructure risks from `knowledge_base/gtm_signals/inboxkit/`

### ACT (20 min)

1. In Cursor (vault open): "Generate this week's MOC using weekly-moc-template"
2. Agent creates `00_foundation/weekly_updates/YYYY-MM-DD.md`
3. Open in Obsidian. Review. Edit "Human Decision Required" checkboxes.

### DEPOSIT (5 min)

1. `git add . && git commit -m "weekly: YYYY-MM-DD — [one-line summary]"`
2. Weekly note stays in graph. Next week's agent sees it in `co-access` queries.
3. Copy note body → paste into email → send to Josh + investors.

---

## Daily Habits (Agent + Human)

### Morning (5 min)

- Check HeyReach unified inbox for replies.
- If reply contains signal (pain confirmed, demo interest, intro offered): create node in `knowledge_base/gtm_signals/heyreach/` with `status: emergent`.
- If reply is negative/no signal: log to `knowledge_base/methodology/OUTREACH_BASELINE_METRICS.md` for elimination tracking.

### As Needed (Agent)

- InboxKit deliverability alert → create `knowledge_base/gtm_signals/inboxkit/` node.
- Linear issue closed → create `knowledge_base/execution/linear/` node.
- New experiment shipped → create `knowledge_base/methodology/experiments/` node.

---

## Monthly (15 min) — Graph Maintenance, Not Governance

1. `context-os graph-exec` — find orphans, check hub health.
2. Archive nodes with `heat: 0` and `status: emergent` for 30+ days.
3. Review `weekly_updates/` folder — older MOCs become canonical citations.
4. **Do NOT:** prune taxonomy, edit ontology, or rewrite governance files. v2 has none.

---

## Tool Scopes (Safety Architecture)

| Tool | Scope | Never Touches | Commit Pattern |
| --- | --- | --- | --- |
| **Cursor** (primary) | `knowledge_base/gtm_signals/`, `00_foundation/weekly_updates/` | `00_foundation/positioning.md` (human-only) | Every agent session |
| **Claude Code** | `knowledge_base/execution/`, CLI queries, graph health | Weekly MOCs (Cursor owns template) | Before/after session |
| **Codex** | `experiment/codex-YYYY-MM-DD/` branches | `main` branch directly | PR to main |
| **Obsidian** | Read + navigate + Canvas dashboards | Never writes via plugins to tracked files | N/A (human interface) |

---

## Emergency: Agent Corruption Recovery

If an agent writes garbage:

1. `git diff` — see exactly what changed.
2. `git checkout -- <file>` — revert single file.
3. If node was overwritten (not just created): restore from previous commit.
4. **Validated nodes (`status: canonical`) are protected by git + human review.**

---

## Multi-Client Replication

For future clients, fork this repo structure:

```text
~/gtm-vaults/
├── kivira-health/          ← This vault
├── client-alpha/           ← Fork, rename, new CLAUDE.md
└── client-beta/
```

Each vault gets:

- Client-specific `CLAUDE.md`
- Same `weekly-moc-template.md` (universal structure)
- Isolated `knowledge_base/` (their graph)
- Shared `gtm-context-os-quickstart/` (upstream skills)

Replication time: 10 minutes per client.

---

**Created:** 2026-05-04  
**Status:** Active  
**Replaces:** `_system/CONTEXT_OS_OPERATING_RHYTHM.md`
