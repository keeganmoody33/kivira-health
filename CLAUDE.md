# Kivira.health — GTM Context OS Navigation Guide

**Purpose:** Central navigation for Kivira’s go-to-market knowledge graph: public corpus, research synthesis, and operational positioning.

---

## What Is This?

This is the **Context Operating System** for Kivira GTM work:

- AI compounds intelligence across sessions via structured nodes and links.
- **Layer 1** holds atomic, reusable concepts; **Layer 2** holds positioning, messaging, and synthesis that *link* to atoms—do not duplicate long explanations in foundation docs.
- **Epistemic rule:** Distinguish **public marketing / legal copy** from **internal or third-party research**. Use tags `source-public-web`, `source-research-synthesis`, and evidence lines `[VERIFIED: …]` / `[INFERRED: …]` / `[UNVERIFIABLE]` per node.

---

## Directory Structure

```text
KIVIRA.HEALTH/
├── CLAUDE.md                          # ← YOU ARE HERE
├── raw-context/                       # Raw ingests (not the graph)
│   ├── MARKETANALYSIS.md
│   └── kivira-public/                 # Firecrawl exports (www + instrument-overview)
│   └── kivira-internal/               # Canonical markdown ingests of internal PDFs/docs (incl. GTM tech stack summary + wishlist; see [[TECH_STACK_OUTBOUND_INFRASTRUCTURE]])
├── knowledge_base/                    # Layer 1: Atomic Knowledge
│   ├── technical/
│   ├── business/
│   ├── methodology/
│   └── emergent/
├── 00_foundation/                    # Layer 2: Operational Docs
│   ├── positioning/
│   ├── messaging/
│   └── _synthesis/
├── _system/
│   ├── knowledge_graph/
│   │   ├── taxonomy.yaml
│   │   └── ontology.yaml
│   ├── agent_workflows/               # Canonical workflow specs for repo-local automations
│   ├── GRAPH_HEALTH_REPORT.md      # Latest health check output
│   └── CONTEXT_OS_OPERATING_RHYTHM.md
├── .claude/                           # Repo-local Claude skills that wrap canonical workflows
├── tam_builder/                       # Python package for TAM builder + CoCM wedge
├── scripts/                           # Thin CLI entrypoints
├── fixtures/                          # Synthetic-first CSV fixtures
├── tests/                             # Automated contract and behavior tests
└── gtm-context-os-quickstart/         # Upstream quickstart (reference; .claude commands)
```

---

## How to Use This System

### Finding information — FAST PATH

**Always start with `_system/GRAPH_INDEX.md`** — a generated fast-lookup index covering:

- **Path Map**: every node name → exact file path (one line, grep-able)
- **Node Registry**: domain / type / status / description / inbound-link count
- **Backlink Index**: for any node, what links to it and what it links to
- **Orphans, Taxonomy Issues, Tag Frequency** in one read
- **Agent Workflows and Skills** indexed

Refresh the index any time with:

```bash
python scripts/index_graph.py
```

If the index is fresh, skip manual grepping entirely — read the Path Map to find a node, then read that file directly.

### Finding information — manual fallback

1. Start with **`00_foundation/_synthesis/`** for the GTM overview.
2. Drill into **`knowledge_base/`** by domain (`business`, `technical`, `methodology`).
3. Follow **`[[wiki-links]]`** between nodes.

### Adding information

- Ingest raw files: use the quickstart **`/ingest`** flow from `gtm-context-os-quickstart` or manually add nodes using `templates/node_template.md` from that repo.
- After adding nodes, run **`/graph-health`** (or follow `.claude/commands/graph-health.md` in the quickstart).
- For internal operating docs that should drive automations, first create a canonical markdown ingest under `raw-context/kivira-internal/`, then extract durable nodes into `knowledge_base/`.

### Repo-local TAM builder

- **Canonical workflow specs:** `_system/agent_workflows/`
- **Claude wrappers:** `.claude/skills/`
- **Python implementation:** `tam_builder/` and `scripts/kivira_tam_builder.py`
- **Synthetic fixtures:** `fixtures/`
- **Tests:** `tests/`

### Codex / Claude Code split

- **Codex:** Python scripts, tests, CSV contracts, workflow docs, and repo audits.
- **Claude Code:** ingestion, knowledge node maintenance, messaging/diligence outputs, and use of repo-local skills during GTM work.
- Keep workflow logic canonical in `_system/agent_workflows/`; wrappers and scripts should reference that source of truth instead of duplicating policy.

### Kivira-specific conventions

- **Clinical / regulatory language:** When describing the product, align with public legal copy: **clinical decision support (CDS)**, not autonomous diagnosis; cite patient app terms / privacy where relevant.
- **Buyer:** B2B to clinics/health systems; patient app free to patients (per public terms).
- **Canonical research synthesis:** `raw-context/MARKETANALYSIS.md` is the maintained source of truth. The repo-root `MARKETANALYSIS.md` is only a pointer to avoid duplicate edits.

---

## Quality Standards

**Every concept should have:**

- Complete YAML frontmatter (`domain`, `node_type`, `status`, `tags`, `source`, `related_concepts`).
- At least **three** `related_concepts` links where possible (emergent nodes may start with fewer per ontology).
- Clear **source** attribution (`source.type`, `source.file` or URL).

---

**Created:** 2026-04-03  
**Status:** Active

---

## AGENT CONSTRAINTS (Hard Rules — All Tools)

1. **NEVER modify files in `00_foundation/positioning/` or `00_foundation/messaging/` without explicit human approval.** These are Layer 2 strategic docs. Agents compose from them; they do not rewrite them.

2. **NEVER delete nodes with `status: validated` or `status: canonical`.** Archive by moving to `knowledge_base/_archive/` and updating frontmatter to `status: archived`.

3. **ALWAYS commit before and after agent sessions.**

   ```bash
   git add -A && git commit -m "pre-agent: [tool-name] session"
   # ... agent work ...
   git add -A && git commit -m "post-agent: [description]"
   ```

4. **NEVER write to branches other than `main` without explicit instruction.** Codex experiments use `experiment/codex-YYYY-MM-DD/` branches.

5. **When in doubt, create — do not overwrite.**

   - New insight → new node with `status: emergent`
   - Updated insight → new node + link to old node + mark old as `status: superseded`
   - Never edit a validated node's body to contradict its original evidence.

6. **Weekly MOC is read-only composition.** The agent creates `00_foundation/weekly_updates/YYYY-MM-DD.md` by **linking** to existing nodes. It does not invent signal data in the weekly.

7. **Evidence discipline enforced.**

   - Every claim in a weekly MOC must link to a node with `source:` frontmatter.
   - If no source node exists, the claim is flagged `[UNVERIFIABLE]` and the human decides.

8. **No taxonomy.yaml obedience.** Agents do not read `_system/knowledge_graph/taxonomy.yaml` or `ontology.yaml`. These are v1 artifacts. Agents use graph heat, inbound links, and co-access to navigate.

---

## TOOL-SPECIFIC SCOPES

### Cursor (Primary GTM Agent)

- **Can:** Create signal nodes, generate weekly MOCs, run graph queries, draft copy variants.
- **Cannot:** Edit positioning v1, delete validated personas, modify TAM tier files.

### Claude Code (Secondary / Infrastructure)

- **Can:** Ingest meeting notes, run `context-os` CLI, build execution nodes, audit graph health.
- **Cannot:** Generate weekly MOCs (Cursor owns template), edit HeyReach copy without human review.

### Codex (Experimental / Python)

- **Can:** Build scripts, run TAM builder, generate CSV fixtures, test automation.
- **Cannot:** Write to `main` branch directly. All code goes through PR review.

---

## HUMAN OVERRIDE

If any agent produces output that contradicts:

- Public legal copy (`raw-context/kivira-public/legal-*`)
- Clinical/regulatory framing (`CDS_NOT_DIAGNOSIS_FRAMING`)
- Investor-facing claims in approved weekly MOCs

**Immediate halt.** Revert commit. Flag in `#gtm-alerts` Slack channel. Human rewrites.

---

**Amended:** 2026-05-04  
**Applies to:** All AI agents operating on Kivira Context-OS
