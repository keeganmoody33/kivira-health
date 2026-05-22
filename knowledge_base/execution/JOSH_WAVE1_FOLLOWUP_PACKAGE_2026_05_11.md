---
name: JOSH_WAVE1_FOLLOWUP_PACKAGE_2026_05_11
description: Operational deposit for Wave 1 LinkedIn accept triage and 10-person follow-up cohort — synthesis folder, scripts, and linked graph evidence nodes.
domain: methodology
node_type: case-study
status: emergent
last_updated: 2026-05-22
tags:
  - methodology
  - gtm-motion
  - outbound
  - source-internal-doc
topics:
  - gtm-motion
  - workflow
  - discovery-calls
related_concepts:
  - "[[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]]"
  - "[[KIVIRA_OUTBOUND_MESSAGE_PATTERN_2026_05_12]]"
  - "[[KIVIRA_OUTBOUND_MESSAGE_PATTERN_V6_2026_05_20]]"
  - "[[WEEKLY_HEYREACH_EVIDENCE_2026_05_20]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
source:
  type: internal-doc
  file: "raw-context/kivira-internal/wave1-josh-followup-package-2026-05-11.md"
  date: "2026-05-11"
---

# Josh Wave 1 follow-up package (2026-05-11)

Synthesis bundle for reviewing and sending LinkedIn follow-ups after Wave 1 connection accepts. Human review package for Josh; execution stays on Keegan's HeyReach sender (`keeganmoody33@gmail.com`).

[VERIFIED: Accept counts and sub-tier mapping from `00_foundation/_synthesis/josh-followup-2026-05-11/accepts-subtier-mapped.md` (58 rows, 2026-05-11 pull).]

## Artifact map

| Artifact | Path |
|----------|------|
| Start here (Josh) | `00_foundation/_synthesis/josh-followup-2026-05-11/messages-josh-preview.md` |
| Accept triage table | `…/accepts-subtier-mapped.md` |
| CSV | `…/accepts-subtier-mapped.csv` |
| Research + v5 commentary | `…/followup-message-template.md` |
| Canonical ingest pointer | `raw-context/kivira-internal/wave1-josh-followup-package-2026-05-11.md` |

## Operator workflow

1. Skim **accepts-subtier-mapped.md** — send only **H** / **M** confidence in-scope rows; **L** needs a 30-second site check.
2. Use **messages-josh-preview.md** for paste-ready v6/v7 copy and send-state (as of 2026-05-20).
3. Pull fresh accepts every week: `scripts/heyreach_accepts_pull.py` (REST; do not rely on UI alone).

## Distilled outcomes (graph elsewhere)

- **17% in-scope** (10/58) — see [[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]].
- **Baseline campaign** drove most vendor/recruiter noise — tighten anti-persona before scaling volume.
- **Follow-up execution** (4/10 touched by 2026-05-20; Oltmans demo booked then missed) — see [[WEEKLY_HEYREACH_EVIDENCE_2026_05_20]].
- **Message pattern** v5 validated; v6 adds first-name greeting + named Maria demo line — see [[KIVIRA_OUTBOUND_MESSAGE_PATTERN_V6_2026_05_20]].

## Top-priority in-scope contact

Yarly Fassih-Nia (WellMed, 1C, Sr Dir Quality & Risk Adjustment) — closest match to intended Operational Owner on the accept list.

## Related Concepts

- [[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]] — What fit vs noise; Wave 2 list-filter implications
- [[KIVIRA_OUTBOUND_MESSAGE_PATTERN_2026_05_12]] — v5 five-beat DM shape
- [[KIVIRA_OUTBOUND_MESSAGE_PATTERN_V6_2026_05_20]] — v6 send variant used in preview
- [[WEEKLY_HEYREACH_EVIDENCE_2026_05_20]] — Live send-state and demo miss
- [[GTM_TIER_ARCHITECTURE_9_SUBTIERS]] — Sub-tier definitions for mapping accepts
