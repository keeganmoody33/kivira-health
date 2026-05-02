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

```
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
