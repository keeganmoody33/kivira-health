---
name: OUTREACH_BASELINE_METRICS
description: Minimal measurement spec for outbound so we can learn which subtiers/personas/messages generate signals and booked demos.
domain: methodology
node_type: framework
status: validated
last_updated: 2026-05-12
tags:
  - methodology
  - outbound
  - metrics
  - buyer-diligence
  - source-research-synthesis
related_concepts:
  - "[[DEMO_FIRST_OUTBOUND_STRATEGY]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
  - "[[PAIN_SEGMENT_MATRIX]]"
  - "[[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]]"
  - "[[KIVIRA_OUTBOUND_MESSAGE_PATTERN_2026_05_12]]"
source:
  type: research-synthesis
  file: "raw-context/kivira-internal/jp-km-outbound-strategy-meeting-notes-2026-04-07.md"
  date: "2026-04-07"
---

# Outreach baseline metrics

[INFERRED: We need a measurable baseline (volume → signals → meetings) to know what’s working and to prune personas/roles that consistently miss.]

## Purpose

- Establish a baseline for outreach performance so iteration is data-driven.
- Support **elimination**: if a role/title bucket consistently produces no signals, remove it from future campaigns.

## Minimal event/metric set (V1)

### Activity volume

- **Accounts targeted**: count of unique accounts in the wave
- **Contacts targeted**: unique contacts attempted
- **Touches sent**: by channel (email, LinkedIn, phone)

### Signals (leading indicators)

- **Replies**: count, positive/neutral/negative
- **Connection accepts** (LinkedIn)
- **Call connects / voicemail pickups**
- **Forward/intro offered** (someone routes you to the right owner)

### Outcomes (what we actually want)

- **Demos booked**: count
- **Demos held**: count
- **Qualified signal**: explicit confirmation of pain / active initiative / budget owner identified

## Key cuts (how to analyze)

- By **subtier** (1A/1B/1C…)
- By **persona role** (operational owner, clinical champion, economic buyer, technical gatekeeper, BH/quality influencer)
- By **message theme** (e.g., ROI/revenue vs outcomes vs workflow)
- By **channel** (email vs LinkedIn vs phone)

## Guardrails

[UNVERIFIABLE: "industry standard sub-2% reply rate" is mentioned in discussion; treat as directional and validate externally before using as a target.]

## Wave 1 actuals (2026-05-04 launch through 2026-05-12)

[VERIFIED: pulled live via `scripts/heyreach_weekly_pull.py` on 2026-05-12.]

### Activity volume

| Metric | Value |
|---|---:|
| Accounts loaded across 3 campaigns | 1,218 |
| Touches in flight (connection requests sent) | 241 |
| Sender count (LinkedIn accounts) | 1 |
| Daily-cap throttle | ~25 connection requests / sender / day |

### Signals (leading)

| Metric | Value |
|---|---:|
| Lifetime accepts (3 campaigns) | 58 |
| Lifetime replies (correspondent-last) | 27 |
| Post-launch replies (since 5/4) | 7 |
| Unread reply threads needing action | 7 |
| Warm/positive replies (qualitative read) | 2 (Vineet Mishra at HCLTech as connector, Scott Lincoln at Mink Group) |
| Counter-pitch / spam replies | 6 |

### Sub-tier-fit ratio (Wave 1 baseline)

- **In-scope accepts / total accepts = 10 / 58 = 17%.** This is the first datapoint for Kivira's accept-quality baseline. Treat this as the bar Wave 2 must beat.
- **Noise composition** of the 48 OUT_OF_SCOPE: ~26 GTM-tooling vendors, ~5 recruiters / agencies, ~9 off-industry sales, ~8 healthcare-adjacent-but-wrong-wedge. See [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]] §Anti-Persona Patterns for the title-pattern filters that should remove most of this at list-build time.

### Outcomes

| Metric | Value |
|---|---:|
| Demos booked | 0 (signal-read window Saturday May 17 — 7 days post-toggle) |
| Demos held | 0 |
| Qualified pain signals | 0 confirmed; pipeline of 10 in-scope follow-ups going out this week |

### Operating learnings affecting future baselines

- **HeyReach `excludeInOtherCampaigns` flag stall (5/3 - 5/10):** persona campaigns silently sent zero outreach for 6 days because of a sticky exclusion-flag interaction between campaigns. Diagnosed 5/10, toggled off 5/11; ClinicalChampion campaign moved from 35 in-flight to 60 in-flight within 24 hours of the toggle, confirming the unblock. **First clean persona-attributable reply-rate read is 2026-05-17.**
- **5-minute REST pull catches stalls daily-inbox checks don't.** `scripts/heyreach_weekly_pull.py` is now part of the Friday ritual.
- **The 17% in-scope baseline is artificially low** because the Baseline-9Subtier campaign over-indexed on generic LinkedIn slices. With Wave 2 anti-pattern filters applied, the realistic in-scope target is **≥40%** at the same volume. Set that as the bar.

### Forward target (Wave 2)

| Metric | Target |
|---|---:|
| Senders attached | 2-3 by end-week 2026-05-18 |
| Daily connection-request capacity | ~50-75 / day (vs ~25 today) |
| In-scope ratio | ≥40% (vs 17% Wave 1 baseline) |
| Demos booked from in-scope cohort | ≥2 by 2026-05-31 |
