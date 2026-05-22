---
name: OPERATIONAL_LIST_VS_STRATEGIC_TAM
description: Distinguishes CMS-deduped strategic TAM logo counts from state NPPES operational list rows produced by the GTM pipeline—never interchange without reconciliation.
domain: methodology
node_type: framework
status: emergent
last_updated: 2026-05-22
tags:
  - methodology
  - tam-total-addressable-market
  - workflow
  - market-segmentation
topics:
  - tam-total-addressable-market
  - workflow
  - market-segmentation
related_concepts:
  - "[[TAM_COMPLETE_698M_ALL_TIERS]]"
  - "[[TAM_DEDUP_METHODOLOGY]]"
  - "[[PUBLIC_DATA_SOURCES_TAM]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[LIST_BUILD_ACCESSIBILITY_FIRST]]"
source:
  type: notes
  file: "agent-transcript/70fb541d-c48a-4f21-954d-63f15e578d3c"
  date: "2026-05-22"
---

# Operational list vs strategic TAM

Kivira uses two different “account counts” that are easy to conflate in conversation and in `output/` CSVs.

## Two layers

| Layer | What it is | Typical use | Example (session 2026-05-22) |
|-------|------------|-------------|-------------------------------|
| **Strategic TAM** | Deduped logos + dollar TAM from CMS/AHA methodology | Board, investor, wedge sizing | **8,435** logos, **$698.9M** ([[TAM_COMPLETE_698M_ALL_TIERS]]) |
| **Operational list** | State-scoped NPPES (and pipeline) rows after seed + classify | Crawl, enrich, wave export | **~54k** GA classified rows; **~52k** tagged 1A in pilot slice |

[VERIFIED: 8,435 / $698.9M from [[TAM_COMPLETE_698M_ALL_TIERS]].]  
[INFERRED: ~54k / ~52k GA operational counts from agent session pipeline runs — not reconciled to national subtier logo table.]

## Why they diverge

- **Geography:** Strategic TAM is national; operational runs are often **single-state** (e.g. GA+NC seed, then GA-only reclassify).
- **Dedup:** Strategic TAM applies [[TAM_DEDUP_METHODOLOGY]] (gross 13,424 → net 8,435). Operational seed is **NPI/org grain**, not pre-deduped to one logo per health system.
- **Classifier behavior:** NPPES org types can concentrate tags (e.g. many GA rows → **1A**) without matching national **2,350** 1A logos.
- **Channel gap:** Operational row count says nothing about **website/email** fill; strategic TAM “reachable pilot” (~1,000–1,280 logos) is a **fit + accessibility** slice, not `COUNT(rows)`.

## Key points

- **TAM estimate documents** ([[TAM_COMPLETE_698M_ALL_TIERS]], tier nodes, `raw-context/kivira-tam-docs/`) are the source for **logo / $ / contact** planning questions.
- **`output/accounts_classified_*.csv`** is the source for **pipeline throughput and QA**—not for asserting national subtier logo totals.
- Reconciliation requires explicit join keys (NPI, CMS CCN, system parent) and dedup rules—not row-count equality.

## Evidence

> "How many accounts by subtier, tier, and total?" — clarified as **TAM docs**, not pipeline CSVs; operational GA file was ~54k rows vs 8,435 national logos.

## Related concepts

- [[TAM_DEDUP_METHODOLOGY]] — how strategic logos are counted once
- [[PUBLIC_DATA_SOURCES_TAM]] — what NPPES contributes vs what TAM PDFs validate
- [[LIST_BUILD_ACCESSIBILITY_FIRST]] — why operational lists can be large yet wave-ready = 0
