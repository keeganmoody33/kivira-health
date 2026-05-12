---
name: ACO_BLITZ_2026_05_W2_PLAN
description: Manual email + phone blitz on a focused ACO target list — 2-hour synchronous blocks with Josh, intended to test whether the 2A buying motion is reachable on a sync cadence that Wave 1's LinkedIn warm-async motion did not surface.
domain: methodology
node_type: framework
status: emergent
last_updated: 2026-05-12
tags:
  - methodology
  - gtm-motion
  - outbound
  - workflow
  - source-internal-doc
topics:
  - gtm-motion
  - workflow
  - execution-cadence
  - market-segmentation
related_concepts:
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]]"
  - "[[OUTBOUND_TWO_CHANNEL_POSTURE_2026_05_12]]"
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
  - "[[OUTREACH_BASELINE_METRICS]]"
source:
  type: notes
  file: "Session conversation 2026-05-12 (Josh text msg + Keegan + Claude planning)"
  date: "2026-05-12"
---

# ACO blitz — Wave 2 sync motion plan (2026-05-12)

A focused, manual email + phone push on a targeted ACO list, run in 2-hour synchronous blocks with Josh. Designed to test a hypothesis that Wave 1's LinkedIn warm-async motion cannot test on its own.

[INFERRED: Plan articulated 2026-05-12 in response to Josh's text — *"there is a focus list of manual email/ phone on a targeted ACO list we can plan to use 2 hours this week to blitz"*. Target list still being constructed at time of writing.]

## The hypothesis being tested

Wave 1's `OperationalOwner` campaign loaded 359 leads tagged as 2A ACOs and produced **zero directly in-scope accepts** after 7+ days of warm LinkedIn outreach (see [[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]] §2A zero-hit observation). Two non-exclusive explanations:

1. **List-quality issue:** the 2A list captured administrative shell-org titles rather than operating Population Health / Care Coordination directors.
2. **Cadence issue:** ACO operators don't manage LinkedIn DMs the way 1C VBC provider operators do, and the warm-async cadence will never produce signal for this sub-tier regardless of list quality.

The blitz tests (2). If a manual email + phone touch produces ≥1 qualified conversation from a comparable-quality ACO list in 1-2 sessions, the bottleneck is cadence. If it also produces nothing, the bottleneck is list-quality and we re-build with stricter CMS-public-file filters.

## Channel specs

- **Channels:** direct email + phone. No LinkedIn touch on these accounts (avoid double-touching from the LinkedIn campaigns).
- **Format:** 2-hour synchronous block with Josh. Sequence: research → email → wait 5 min → phone. Move to next account if no pickup; voicemail + email follow-up combo.
- **Initial cadence:** twice this week (target completion before 2026-05-18).
- **Volume per block:** ~10-15 accounts touched per 2-hour session, depending on call-time and email-personalization depth.

## Target list construction

Separate from Wave 1's 359-lead 2A pool — that list is in HeyReach campaign 416316 and has already been touched.

**Sourcing rules:**

- CMS MSSP and ACO REACH participant public-use files as the primary spine.
- Entity must be an *operating* ACO (not a holding/administrative shell — see [[GTM_TIER_ARCHITECTURE_9_SUBTIERS]] Tier 2A "Exclude if" criteria).
- ≥1,000 covered lives (raise the floor from Wave 1's 500-cover-life setting to filter administrative shells).
- Identifiable Director / VP-level Population Health, Care Coordination, Quality, or Risk Performance operator on LinkedIn or in public org listings — at the *participant entity*, not at a parent health system.
- Email and phone enrichment via Clay or Apollo before the block starts (don't burn block time on enrichment).

**Intended size:** 30-50 accounts for the first two blocks (gives ~3-5 accounts of buffer per block in case some are unreachable or get bounced).

## Copy + script outline

The blitz email is **not** the v5 LinkedIn DM pattern. Different medium, different constraint:

- **Subject line:** specific to their org. Something like *"[Org name] Stars / risk adjustment + behavioral health"* or *"PCP behavioral health workflow at [Org]"*. No generic subject.
- **Body:** ~80-120 words. Lead with the named-funder social proof (*"Backed by Antler, funded by Wellstar Catalyst"*), one sentence on the role-specific value-prop tied to ACO performance, founder + Josh available for a 15-minute call. No connection-request preamble.
- **Phone script:** 30-second hook → ask if it's a fit conversation → if yes, schedule on the call; if no, get the right name for the team.

Draft copy goes into `00_foundation/_synthesis/aco-blitz-2026-05-week-of/` when the blocks start. **HeyReach copy review HARD RULE does not apply** to this channel — these emails go out from Josh's or Keegan's direct email, not via HeyReach.

## Success criteria

- **Primary:** ≥1 qualified discovery call booked from the blitz cohort by 2026-05-31.
- **Secondary:** Phone connect rate ≥10% across attempted dials. Email open rate ≥30%. Reply rate ≥5%.
- **Threshold for "the cadence is the bottleneck":** ≥1 qualified call from ≤30 attempts. If we hit that, ramp the blitz.
- **Threshold for "the list is the bottleneck":** zero qualified calls from 30+ attempts, AND the LinkedIn 2A campaign continues to produce zero in-scope at higher volume. Then rebuild the 2A list with the stricter rules above.

## What this plan does NOT include

- Does not commit to a permanent blitz channel. This is a 1-2 session test.
- Does not replace the LinkedIn motion for 2A — both run in parallel (see [[OUTBOUND_TWO_CHANNEL_POSTURE_2026_05_12]]).
- Does not pull in Josh for LinkedIn copy review during the test window — that's separate workflow.
- Does not extend to 3A health systems or 1C VBC providers in this iteration. ACO-only.

## Open questions to resolve before the first block

1. Who owns the focus-list build before the block? (Josh? Keegan? Clay automation?)
2. What's the call-tool for the synchronous blocks (direct dial from cell? Aircall? Dialpad?)?
3. Are we recording calls for replay / training, or just notetaking live?
4. Where do qualified-call outcomes get logged? (Linear ticket? CRM-deferred until the 5/15 CRM decision?)
