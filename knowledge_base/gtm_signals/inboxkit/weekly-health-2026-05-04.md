---
name: WEEKLY_INBOXKIT_HEALTH_2026_05_04
description: Domain and mailbox warmup health snapshot from InboxKit Production API sweep
domain: business
node_type: gtm_signal
status: emergent
evidence_date: 2026-05-04
tags:
  - inboxkit
  - weekly-evidence
  - email-deliverability
topics:
  - outbound
related_concepts:
  - "[[TECH_STACK_OUTBOUND_INFRASTRUCTURE]]"
  - "[[OUTREACH_BASELINE_METRICS]]"
  - "[[OUTREACH_WAVE_STRUCTURE]]"
  - "[[WAVE_1_SCORING_FRAMEWORK]]"
source:
  type: api_snapshot
  system: inboxkit
  date: "2026-05-04"
  note: Responses from GET/POST `/v1/api/*` (domains list, mailboxes list, warmup list); captured during `scripts/inboxkit_api_smoke.sh` sweep in local environment dated 2026-05-04
---

# InboxKit Health — May 4

[VERIFIED: Snapshot from InboxKit Production API dated 2026-05-04 — domains `/v1/api/domains/list`, mailboxes `/v1/api/mailboxes/list`, warmup `/v1/api/warmup/list` with bearer auth and `X-Workspace-Id`; 16 warmup subscriptions aligned to 16 active mailboxes.]

Aggregate for this workspace on the pull date: **8** active domains, **16** mailboxes, **16** warmup subscriptions (all `in_progress`), cached `warmup_day` **8**, cached `health_score` **98.4** across polled mailboxes. Two parked domains (**groundskeep.xyz**, **scuttlewutt.com**) have **zero** assigned mailboxes in this snapshot.

| Domain | Mailboxes | Warmup Day | Health Score | Status |
|--------|-----------|------------|--------------|--------|
| groundskeep.xyz | 0 | — | — | active domain / no mailboxes |
| kivira.online | 3 | 8 | 98.4 | warmup in_progress |
| kivira.xyz | 3 | 8 | 98.4 | warmup in_progress |
| kivirahealth.info | 2 | 8 | 98.4 | warmup in_progress |
| kivirahealth.live | 2 | 8 | 98.4 | warmup in_progress |
| kivirahealth.online | 3 | 8 | 98.4 | warmup in_progress |
| kivirahealth.xyz | 3 | 8 | 98.4 | warmup in_progress |
| scuttlewutt.com | 0 | — | — | active domain / no mailboxes |

## Interpretation

Operational send capacity is anchored on the six Kivira-branded domains with assigned mailboxes; warmup progression is homogeneous on **day 8** with stable `health_score` readings in cached stats. Re-hit the API week-over-week rather than extrapolating from cached fields alone.

Linked procedures: **`scripts/inboxkit_api_smoke.sh`** for repeat pulls; [[TECH_STACK_OUTBOUND_INFRASTRUCTURE]].
