---
name: WEEKLY_MOC_GRAPH_RITUAL
description: Weekly email as graph operation—the MOC is a citation hub that heats evidence nodes via explicit wikilinks; investor email is the side effect of tightening backlinks.
domain: methodology
node_type: framework
status: validated
last_updated: 2026-05-11
tags:
  - methodology
  - weekly-moc
  - context-os
  - evidence-discipline
topics:
  - gtm-motion
  - workflow
related_concepts:
  - "[[EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS]]"
  - "[[OUTREACH_BASELINE_METRICS]]"
  - "[[TECH_STACK_OUTBOUND_INFRASTRUCTURE]]"
  - "[[GTM_30_60_90_EXECUTION_CADENCE]]"
source:
  type: document
  file: "knowledge_base/methodology/WEEKLY_MOC_GRAPH_RITUAL.md"
  date: "2026-05-04"
---

# Weekly MOC as graph operation

The weekly update to Josh or investors is **not** a standalone memo written *about* the knowledge graph. It is a **graph operation you perform inside the graph**: each week you wire the hub (the dated MOC) to that week's **evidence nodes** so claims stay auditable and orphans do not accumulate.

## Jacob's pre-send graph tightening (~15 minutes)

1. **Heat the evidence nodes** — Ensure the weekly file explicitly links to every evidence node you minted for that week (HeyReach, Linear, InboxKit, or other surfaces). **Inbound links** from the MOC are what give those nodes sustained relevance in `_system/GRAPH_INDEX.md` backlink views.
2. **Make the MOC a hub** — Add an **Evidence This Week** (or equivalent) block near the top that lists each evidence node as a real Context OS wikilink so `scripts/index_graph.py` can resolve backlinks.
3. **Frontmatter `name:`** — Give each weekly file a stable wiki id, e.g. `name: WEEKLY_MOC_2026_05_04`, so other nodes can reference that hub id in wikilink form and resolve symmetrically in `_system/GRAPH_INDEX.md`.
4. **Then** generate the investor email; the send-ready copy is a **side effect** of the linking step—not the other way around.

## Rules that match automation

- Claims in the MOC body should **link** to nodes that carry `source:` provenance, or be explicitly flagged `[UNVERIFIABLE]` (per [[EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS]] and CLAUDE.md).
- Prefer **verbatim** weekly-evidence wikilinks in the Markdown body (node id pattern like `WEEKLY_HEYREACH_EVIDENCE_2026_05_04`). **Display aliases** (Obsidian pipe syntax like `[[NAME|alias]]`) are also indexed — the indexer captures the first segment before `|` and resolves it against the node `name:` map.
- Optional sibling `YYYY-MM-DD-investor-email.md` remains non-authoritative for new numbers—numbers flow **from evidence nodes → MOC → email**.

## Cross-links from evidence back to the MOC

Each weekly evidence node should list that week’s hub id (e.g. `WEEKLY_MOC_2026_05_04`) under `related_concepts` **for that week** so the relationship is bidirectional in the index.

## Related

- [[OUTREACH_BASELINE_METRICS]] — what “good” looks like once evidence is warm.
- [[TECH_STACK_OUTBOUND_INFRASTRUCTURE]] — where tool evidence nodes fit in the stack story.
