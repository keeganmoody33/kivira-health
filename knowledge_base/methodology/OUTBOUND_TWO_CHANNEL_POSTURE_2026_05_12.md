---
name: OUTBOUND_TWO_CHANNEL_POSTURE_2026_05_12
description: Strategic framing for running LinkedIn (warm/async) and ACO blitz (manual/sync) as parallel outbound motions — complementary, not redundant, deliberately testing two buying cadences in parallel.
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
related_concepts:
  - "[[OUTREACH_BASELINE_METRICS]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[ACO_BLITZ_2026_05_W2_PLAN]]"
  - "[[ACO_ATTACK_MOTION_2A_PRIMARY]]"
  - "[[OUTBOUND_SENDER_RAMP_2026_05_W2]]"
  - "[[KIVIRA_OUTBOUND_MESSAGE_PATTERN_2026_05_12]]"
source:
  type: notes
  file: "Session conversation 2026-05-11 → 2026-05-12 (Keegan + Claude)"
  date: "2026-05-12"
---

# Outbound two-channel posture (2026-05-12)

Kivira runs outbound on two parallel channels with different cadences, staffing, and target shapes. They are not sequential phases of the same funnel; they are independent experiments running side-by-side because each one tests a different buying motion.

[VERIFIED: Posture decided in 2026-05-12 outreach planning session and reflected in the 2026-05-11 weekly investor email §5.]

## The two channels

| | **LinkedIn (warm async)** | **ACO blitz (manual sync)** |
|---|---|---|
| **Cadence** | Day-cap throttled (~25/sender/day at v1); responses arrive whenever the recipient checks LinkedIn. | 2-hour synchronous blocks (initially with Josh, twice this week as test). Calls happen live. |
| **Staffing** | One operator can run multiple senders concurrently via HeyReach. | One operator per block; needs Josh's time directly. |
| **Cost per touch** | ~$0 incremental; cost is sender-account warm-up + tooling subscription. | High — direct executive time on every dial / personalized email. |
| **Signal type** | Accept rate, reply rate, in-scope ratio. Lagging by 5-10 days. | Phone connect, voicemail pickup, immediate conversational signal. Sub-24h. |
| **Ideal target** | Sub-tiers where the buying motion is async-friendly (1A, 1C, 2C, 3C — operators / clinical champions who manage their LinkedIn). | Sub-tiers where the buying motion needs synchronous depth (2A ACOs — see hypothesis below). |
| **Scale ceiling** | Unbounded by sender count + warm-up runway; tracks toward 75-100/day at 3 senders. | Hard bounded by Josh's time — ~10-15 conversations per 2-hour block. |
| **What it tests** | Whether targeted persona × sub-tier matching produces in-scope warm conversations at scale. | Whether the 2A ACO buying motion is *reachable at all* on a different cadence than warm async. |

## Why parallel, not sequential

The naive default is "run LinkedIn first, then if it works ramp; if not, try blitz." That sequencing wastes weeks because LinkedIn signal-reads are lagging (5-10 days per cycle). Running both in parallel:

1. **Halves time-to-learning.** If 2A ACO is unreachable async (Wave 1 evidence: zero in-scope hits from the 359-lead OperationalOwner-2A campaign — see [[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]]), we learn that via the blitz in days, not weeks.
2. **Different evidence types compound.** LinkedIn produces accept-quality + reply-rate signal across sub-tiers. The blitz produces phone-connect / voicemail-conversion signal on one specific sub-tier (2A). The two together tell us where the buying motion is, not just which channel works.
3. **Failure modes are independent.** LinkedIn stalls (the 5/3–5/10 exclude-flag stall) don't pause the blitz. Blitz fatigue (Josh's bandwidth) doesn't pause LinkedIn.

## Triggers for shifting weight between them

- **Shift toward LinkedIn** if Wave 2's in-scope ratio clears the 40% target and reply-rate on the v5 [[KIVIRA_OUTBOUND_MESSAGE_PATTERN_2026_05_12]] template holds above 30%. The async channel is then producing real signal at low marginal cost; ramp senders.
- **Shift toward blitz** if the blitz produces ≥1 qualified discovery call in its first two sessions while LinkedIn signal stays flat. ACO buying motion is reachable on sync, not async — fund the blitz, slow the LinkedIn pipeline.
- **Run both at full weight** until the 2026-05-17 LinkedIn signal-read window closes — that's the first data point that lets us calibrate.

## Anti-patterns (don't do this)

- **Don't sequence them.** Default human bias is "finish one before starting the other." Both motions need ≥7 days to produce signal; sequencing wastes that elapsed time.
- **Don't dilute the LinkedIn message pattern for blitz.** The v5 LinkedIn DM pattern is built for a specific medium. Blitz email + phone copy is a separate artifact (to be authored).
- **Don't have Josh run LinkedIn too.** Sender ramp adds senders (see [[OUTBOUND_SENDER_RAMP_2026_05_W2]]); Josh's time goes to blitz.

## Refresh cadence

Re-evaluate after 2026-05-31 — by then both channels will have had 2-3 weeks of run. If the relative signal-rates have inverted from the current hypothesis, mint a successor node `OUTBOUND_TWO_CHANNEL_POSTURE_<next-date>` rather than overwriting this one.
