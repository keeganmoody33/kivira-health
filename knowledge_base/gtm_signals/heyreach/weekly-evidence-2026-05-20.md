---
name: WEEKLY_HEYREACH_EVIDENCE_2026_05_20
description: HeyReach Wave 1 follow-up execution snapshot — 4 of 10 touched, Oltmans demo missed, Wave 2A ACO copy drafted
domain: business
node_type: gtm_signal
status: emergent
date: "2026-05-20"
evidence_date: 2026-05-20
tags:
  - heyreach
  - weekly-evidence
  - outbound
  - wave1
  - wave2a
  - follow-up
topics:
  - gtm-motion
related_concepts:
  - "[[JOSH_WAVE1_FOLLOWUP_PACKAGE_2026_05_11]]"
  - "[[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]]"
  - "[[KIVIRA_OUTBOUND_MESSAGE_PATTERN_V6_2026_05_20]]"
  - "[[WEEKLY_HEYREACH_EVIDENCE_2026_05_10]]"
  - "[[WEEKLY_MOC_GRAPH_RITUAL]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[OUTREACH_WAVE_STRUCTURE]]"
  - "[[CDS_NOT_DIAGNOSIS_FRAMING]]"
  - "[[TECH_STACK_OUTBOUND_INFRASTRUCTURE]]"
source:
  type: tool_export
  system: heyreach-rest
  file: "scripts/heyreach_accepts_pull.py"
  endpoints: "POST /inbox/GetConversationsV2"
  date: "2026-05-20"
---

# HeyReach — Wave 1 Follow-Up Execution (2026-05-20)

[VERIFIED: Pulled via `scripts/heyreach_accepts_pull.py` on 2026-05-20. Workspace accepts: **86** (Δ +28 vs 58 on 2026-05-10). Sender: `keeganmoody33@gmail.com`.]

## Wave 1 In-Scope Follow-Up Cohort (10)

Artifact: `00_foundation/_synthesis/josh-followup-2026-05-11/messages-josh-preview.md` (v7, 2026-05-20).

| # | Name | Org | Follow-up status | Notes |
|---|------|-----|------------------|-------|
| 1 | Yarly Fassih-Nia | WellMed | Sent 5/12 | Ad-lib copy; no reply |
| 2 | Robert Lystrup, MD | ACP | Sent 5/12 (broken) | Apology sent; **clean resend pending** |
| 3 | Chris Oltmans | NxtCare | Sent; **demo booked then missed** | Replied 5/12; Wed 5/20 3:00 PM CST slot **not held** |
| 4 | Jeremy Wigginton, MD | Capital BCBS | Sent 5/12 | Typo lead-in; no reply |
| 5 | Christa Thomas | Optum | **Not sent** | Still on thanks-for-connect |
| 6 | Jason Johnson | Privia | **Not sent** | Still on thanks-for-connect |
| 7 | Lynn LeCluyse | Privia | **Not sent** | Send only after #6 |
| 8 | Chris MacInnis | Old Mission Wound Care | **Not sent** | Site check first |
| 9 | Scott Quinn | EVOS Health | **Not sent** | Site check first |
| 10 | Kumar Murukurthy, MD | Optimum Healthcare IT | **Not sent** | Site check first |

**Headline:** First live demo path (Oltmans) opened from follow-up, then **no-show on operator side**. Six paste-ready v6 drafts remain queued. Lystrup thread needs repair before next touch.

## Wave 2A (Forward Work, Same Deposit)

Synthesis draft (not promoted to `00_foundation/messaging/` — human review required):

- `00_foundation/_synthesis/wave2a-aco-heyreach-copy-2026-05-21/wave2a_aco_heyreach_copy.md`
- Build scripts: `scripts/build_aco_bh_purpose_list.py`, `scripts/build_aco_persona_heyreach.py`
- Fixture: `fixtures/heyreach_loads/heyreach_leads_2a_persona.json`
- SPIDER query runs: `fixtures/wave1_runs/20260521T*`

[INFERRED: Wave 2A addresses the zero in-scope 2A accepts from Wave 1 per `[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]` §Wave 1 accept distribution.]

## Human Decisions Required

- [ ] Oltmans: send reschedule / apology DM
- [ ] Lystrup: resend clean v6 copy
- [ ] Christa → Jason → Lynn send batch after Josh OK on v7 preview
- [ ] Promote Wave 2A copy to messaging layer only after human review

## What This Proves

- Follow-up motion is **manual and fragile** — booking happened; execution discipline is the bottleneck, not copy availability.
- Graph + synthesis deposit (`v7` preview + this evidence node) keeps operator state out of chat-only memory.
- Wave 2A list/copy work started in parallel with Wave 1 follow-up cleanup — correct parallel lane per [[OUTREACH_WAVE_STRUCTURE]].
