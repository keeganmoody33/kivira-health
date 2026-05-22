---
name: OUTBOUND_INBOX_SEND_VOLUME_MATH
description: Monthly cold-email send capacity for Kivira's 6-domain × 3-inbox InboxKit setup — per-inbox caps, 3-touch sequences, warmup ramp, and TAM coverage timelines.
domain: methodology
node_type: framework
status: emergent
last_updated: 2026-05-22
tags:
  - methodology
  - gtm-motion
  - outbound-infrastructure
  - tam-total-addressable-market
topics:
  - outbound-infrastructure
  - gtm-motion
  - execution-cadence
  - workflow
related_concepts:
  - "[[TAM_INBOX_CAPACITY_THREE_PERSONAS]]"
  - "[[OUTREACH_WAVE_STRUCTURE]]"
  - "[[TAM_COMPLETE_698M_ALL_TIERS]]"
  - "[[INBOXKIT_SENDKIT_SEQUENCER_ROADMAP]]"
  - "[[TECH_STACK_OUTBOUND_INFRASTRUCTURE]]"
  - "[[OUTREACH_BASELINE_METRICS]]"
  - "[[THIRTY_DAY_OFFICE_MANAGER_TARGET]]"
source:
  type: notes
  file: "cursor-session outbound-volume-planning 2026-05-22"
  date: "2026-05-22"
---

# Outbound inbox send volume math

Planning reference for **6 domains × 3 inboxes = 18 sending identities** on InboxKit (Google Workspace / Microsoft 365). Send volume is governed by **inbox count × per-inbox daily cap × sending days**, not by sequence length alone.

[INFERRED: Per-inbox caps from cold-email deliverability norms; validate against InboxKit warmup telemetry and healthcare open rates in first 2 weeks of production sends.]

## Per-inbox daily caps (cold outbound)

| Posture | Sends/inbox/day | When to use |
|---------|----------------:|-------------|
| Conservative | 25 | Day 1–60; healthcare deliverability unproven |
| Moderate | 35 | Standard post-warmup steady state |
| Aggressive | 50 | Fully warm inboxes only; Month 3+ if reply rates hold |

Google's **500/day** SMTP ceiling is a technical limit, not a safe cold-outbound target. Plan against **25–50/day per inbox**.

Sending days: **22 weekdays/month** (weekend sends hurt healthcare reply rates).

## Steady-state monthly sends (18 inboxes)

| Posture | Monthly sends |
|---------|----------------:|
| Conservative (25/day) | ~9,900 |
| Moderate (35/day) | ~13,860 |
| Aggressive (50/day) | ~19,800 |

[INFERRED: ~75,000 sends/month would require ~50–60 inboxes (e.g. 6 domains × 9–10 inboxes), not 18.]

## Sequence length vs unique contacts

Sequence length changes **how many unique people** the fixed send budget reaches — not total sends.

With a **3-touch sequence** (operator planning assumption):

| Posture | Monthly sends | Unique contacts/mo (÷ 3) |
|---------|--------------:|-------------------------:|
| Conservative | ~9,900 | ~3,300 |
| Moderate | ~13,860 | ~4,620 |
| Aggressive | ~19,800 | ~6,600 |

At **~2.8 contacts/account** ([[TAM_COMPLETE_698M_ALL_TIERS]] observed ratio), moderate throughput ≈ **~1,650 accounts touched/month**.

## Warmup ramp (first 30 days)

| Phase | Per-inbox/day | Notes |
|-------|-------------:|-------|
| Week 1 | 5 (warmup only) | ~0 prospect sends |
| Week 2 | 15 | Partial cold ramp |
| Week 3 | 25 | Ramping |
| Week 4 | 35 | Near steady state |
| Month 1 cold total | — | ~6,500–7,500 sends |
| Month 2+ steady | 35 | ~13,500–14,000 sends/mo |

Allow **2–4 weeks warmup** before counting inboxes as production cold capacity ([[OUTREACH_WAVE_STRUCTURE]] domain planning).

## TAM coverage (3-touch, moderate, 18 inboxes)

| Scope | Contacts | Time at moderate steady state |
|-------|----------|-------------------------------|
| Wave 1 (1C + 2A high-fit) | ~2,500 | ~3–4 weeks |
| Wave 2 | ~5,000 | ~1 month |
| Wave 3 | ~8,000 | ~1.7 months |
| Full cold TAM (1A–1C, 2A, 2C) | ~21,765 | ~4.7 months |

## Key points

- **Signal > volume** for Day 30: [[THIRTY_DAY_OFFICE_MANAGER_TARGET]] is 5 live conversations, not maximum sends.
- **Instantly Growth** caps at 1,000 active leads — at ~4,600 contacts/mo feed rate, time-slice cohorts or upgrade by Day 60.
- **List quality before ramp:** [[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]] — do not scale sends on a noisy list.

## Evidence

> "I'm sending each individual a sequence of three messages… comes out to be like 75,000 messages" — operator planning question; corrected to ~10K–20K/mo ceiling on 18 inboxes.

## Related concepts

- [[TAM_INBOX_CAPACITY_THREE_PERSONAS]] — logo × persona × inbox capacity framing (distinct from send-rate math)
- [[OUTREACH_WAVE_STRUCTURE]] — wave contact volumes and domain velocity assumptions
- [[INBOXKIT_SENDKIT_SEQUENCER_ROADMAP]] — where warmed mailboxes connect to sequencer
