---
name: TAM_INBOX_CAPACITY_THREE_PERSONAS
description: Operational inbox/domain capacity when planning three personas and three sending inboxes per account location against strategic TAM logo counts.
domain: methodology
node_type: framework
status: emergent
last_updated: 2026-05-22
tags:
  - methodology
  - tam-total-addressable-market
  - gtm-motion
  - outbound-infrastructure
topics:
  - tam-total-addressable-market
  - outbound-infrastructure
  - gtm-motion
  - workflow
related_concepts:
  - "[[TAM_COMPLETE_698M_ALL_TIERS]]"
  - "[[INBOXKIT_SENDKIT_SEQUENCER_ROADMAP]]"
  - "[[OUTREACH_BASELINE_METRICS]]"
  - "[[BUYING_COMMITTEE_DYNAMICS]]"
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
  - "[[OPERATIONAL_LIST_VS_STRATEGIC_TAM]]"
  - "[[OUTBOUND_INBOX_SEND_VOLUME_MATH]]"
  - "[[TAM_BREADTH_DEPTH_TESTING_FRAMEWORK]]"
source:
  type: notes
  file: "agent-transcript/70fb541d-c48a-4f21-954d-63f15e578d3c"
  date: "2026-05-22"
---

# TAM inbox capacity (three personas × three inboxes)

Planning rule for outbound infrastructure: if each **account logo** is approached with **three buyer personas** and each persona (or account location) gets **three dedicated sending inboxes/domains**, total mailbox demand scales as **logos × 3**, not logos × 1.

[VERIFIED: Logo counts from [[TAM_COMPLETE_698M_ALL_TIERS]] and reachable-pilot range from the same node’s View 2.]

## Capacity tables

### National strategic TAM (deduped logos)

| Scope | Logos | Inboxes (×3) |
|-------|------:|-------------:|
| **Total deduped TAM** | 8,435 | **25,305** |
| Tier 1 only | 7,290 | 21,870 |
| Tier 2 only | 675 | 2,025 |
| Tier 3 only | 470 | 1,410 |

### Reachable pilot TAM (outbound-now slice)

| Scope | Logos | Inboxes (×3) |
|-------|------:|-------------:|
| Reachable pilot (low) | ~1,000 | ~3,000 |
| Reachable pilot (high) | ~1,280 | ~3,840 |

[VERIFIED: ~1,000–1,280 logos in [[TAM_COMPLETE_698M_ALL_TIERS]] § View 2: Reachable Pilot TAM.]

### By subtier (national logos → inboxes)

| Subtier | Logos | Inboxes (×3) |
|---------|------:|-------------:|
| 1A | 2,350 | 7,050 |
| 1B | 1,740 | 5,220 |
| 1C | 3,200 | 9,600 |
| 2A | 395 | 1,185 |
| 2B | 100 | 300 |
| 2C | 180 | 540 |
| 3A | 250 | 750 |
| 3B | 80 | 240 |
| 3C | 140 | 420 |

## Key points

- **Personas ≠ inboxes by default.** Three personas per account is a **buying-committee** pattern ([[BUYING_COMMITTEE_DYNAMICS]], [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]). Three inboxes per account is an **infrastructure** assumption used here for capacity math only—confirm against [[INBOXKIT_SENDKIT_SEQUENCER_ROADMAP]] and actual domain/mailbox policy.
- **Strategic TAM ≠ send-ready list.** Logo counts above are **market sizing**; they do not imply every logo has email, website, or wave-ready contacts. See [[OPERATIONAL_LIST_VS_STRATEGIC_TAM]] and [[LIST_BUILD_ACCESSIBILITY_FIRST]].
- **Wave 1 noise scales with bad lists.** [[OUTREACH_BASELINE_METRICS]] and [[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]] show list quality drove ~83% out-of-scope accepts; adding inboxes before tightening list filters scales noise, not learning.

## Evidence

> "If 3 personas per account and 3 inboxes per domain [per account], run the numbers" — operator planning question, agent session 2026-05-22.

## Related concepts

- [[TAM_COMPLETE_698M_ALL_TIERS]] — authoritative logo and dollar TAM tables
- [[INBOXKIT_SENDKIT_SEQUENCER_ROADMAP]] — where mailbox/domain capacity lands in stack
- [[OUTREACH_BASELINE_METRICS]] — Wave 1 actuals; sender ramp order vs list quality
- [[OPERATIONAL_LIST_VS_STRATEGIC_TAM]] — do not confuse NPPES row counts with 8,435 logos
