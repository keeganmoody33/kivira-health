---
name: HEAT_EXCEPTION_EXTERNAL_VALIDATION
description: Heat (inbound link count) is the default v2 lifecycle signal, but it undercounts importance for nodes representing external press, third-party validation, publicity, or strategic positioning. These node types require manual review before any heat-based archive decision.
domain: methodology
node_type: principle
status: validated
last_updated: 2026-05-11
date: "2026-05-11"
tags:
  - methodology
  - context-os
  - graph-health
  - evidence-discipline
topics:
  - workflow
related_concepts:
  - "[[EVIDENCE_DISCIPLINE_RESEARCH_SYNTHESIS]]"
  - "[[POLSKY_UCHICAGO_KIVIRA_PROFILE_2026]]"
  - "[[KIVIRA_BACKER_COPY_SHIFT_2026_05]]"
  - "[[FUNDING_AND_BACKING_SIGNALS]]"
source:
  type: principle
  origin: "Session 2026-05-11 — operator surfaced that POLSKY (3 inbound, 36 days old) would auto-archive under the default heat rule but is strategically core."
  date: "2026-05-11"
---

# Heat exception — external validation nodes don't archive on heat alone

## The principle

Context OS v2 retired v1's taxonomy and ontology in favor of **letting heat (inbound link count, co-access patterns) define what's load-bearing**. The Monthly Graph Maintenance rule (per `_system/CONTEXT_OS_OPERATING_RHYTHM.md`) says:

> Archive nodes with `heat: 0` and `status: emergent` for 30+ days.

This default works for the vast majority of nodes — operational frameworks, methodology atoms, signal evidence — because the corpus naturally accumulates citations to load-bearing concepts. But it **systematically undercounts** the importance of one category:

**Nodes whose value is external, not internal.**

## Why heat undercounts external-validation nodes

Internal nodes accrue inbound links because *other internal nodes cite them*. The graph grows organically around concepts that are useful for the work being done. But for nodes like:

- **Third-party press coverage** (e.g., `POLSKY_UCHICAGO_KIVIRA_PROFILE_2026` — a UChicago Polsky Center profile of Kivira)
- **Publicity assets** (awards, certifications, named-customer references)
- **External-relationship snapshots** (a backer copy shift, a partnership announcement)
- **Regulatory citations** (FDA classifications, HIPAA postures captured from external sources)
- **Strategic-positioning nodes** that summarize how a thing is perceived externally

…the citing nodes mostly **don't exist in our corpus yet**. Their value isn't in being cited by 7+ internal frameworks — it's in being **available when the right outbound message, investor deck, or partner conversation needs them**.

`POLSKY` is the canonical example: 3 inbound, 36 days old, would auto-archive under the default rule. But it's also the only third-party validation we have from a top-5 business school's entrepreneurship center. Archiving it would silently delete a real asset.

## The exception rule

When the Monthly Graph Maintenance ritual triggers a heat-based archive decision:

1. **Check the node's `node_type`, `tags`, and `domain`.** If any of the following are present, the node is a candidate for the exception:
   - `node_type: gtm_signal` (when the signal is external)
   - `tags: third-party-press` / `external-validation` / `publicity` / `regulatory-citation`
   - The node's body explicitly cites an external publication, certification, or third-party endorsement
2. **Manual review before archive.** A human (not an agent) decides whether the node still has forward strategic value, even if its inbound count is low.
3. **Default action under uncertainty: keep, don't archive.** External-validation nodes are cheap to keep; the cost of accidentally archiving an irreplaceable third-party reference is high.

## What changes operationally

| Scenario | Default v2 rule | Exception rule |
|---|---|---|
| Emergent + 30 days + 0 inbound + ops/methodology framework | archive | archive (no change) |
| Emergent + 30 days + 0–1 inbound + external-press / publicity | (would archive) | **manual review; default keep** |
| Validated + any age + low heat + external-validation | (no archive — protected) | (no change — protected) |

## Why this isn't a return to v1 taxonomy

V1's failure mode was **upfront schema enforcement** — a blessed list of statuses and node types that rejected anything new. This exception is the opposite: it's an **observation about how the graph actually accrues heat**, not a prescription for what nodes are allowed.

The exception lives in this methodology node (not in the indexer code) so it can evolve. As the corpus grows and more external-validation nodes get cited internally, the heat metric will catch up; at that point this exception may be unnecessary. But for an early-stage corpus where external citations are still being incorporated, the default heat rule overshoots.

## Linked decisions

- `POLSKY_UCHICAGO_KIVIRA_PROFILE_2026` promoted to `validated` on 2026-05-11 by manual override, citing this principle.
- `KIVIRA_BACKER_COPY_SHIFT_2026_05` created 2026-05-11 — an external-positioning signal with low projected inbound but real strategic value.

## How agents should apply this

When generating a Monthly Graph Maintenance report, do NOT include external-validation nodes in the auto-archive list. Instead, surface them in a separate **"External-validation nodes — manual review required"** subsection with the recommendation: *"Keep unless the underlying external reference is stale or rescinded."*
