---
name: OUTBOUND_SENDER_RAMP_2026_05_W2
description: Plan to add 2-3 LinkedIn senders to the HeyReach stack this week, breaking the ~25/day single-sender cap and roughly tripling outbound capacity — only after Wave 2 list filters tighten, never as a way to scale a noisy list.
domain: methodology
node_type: framework
status: emergent
last_updated: 2026-05-12
tags:
  - methodology
  - gtm-motion
  - outbound
  - gtm-tooling
  - workflow
  - source-internal-doc
topics:
  - gtm-motion
  - workflow
  - execution-cadence
related_concepts:
  - "[[OUTREACH_BASELINE_METRICS]]"
  - "[[TECH_STACK_OUTBOUND_INFRASTRUCTURE]]"
  - "[[OUTBOUND_TWO_CHANNEL_POSTURE_2026_05_12]]"
  - "[[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]]"
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
source:
  type: notes
  file: "Session conversation 2026-05-12 (Wave 2 next-steps thread)"
  date: "2026-05-12"
---

# Outbound sender ramp — Wave 2 plan (2026-05-W2)

Wave 1 ran on a single LinkedIn sender (`keeganmoody33`), day-capped at ~25 connection requests / day per HeyReach default. With list-quality tightening for Wave 2 (see [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]] §Anti-Persona Patterns) and the message pattern stabilizing (see [[KIVIRA_OUTBOUND_MESSAGE_PATTERN_2026_05_12]]), the next ramp lever is **send volume**.

[INFERRED: Targets stated in the 2026-05-11 weekly investor email §5; full execution plan first written 2026-05-12.]

## Current state vs. target

| Metric | 2026-05-12 (current) | 2026-05-18 (target) |
|---|---:|---:|
| Senders attached to HeyReach | 1 | 2-3 |
| Sender identity | `keeganmoody33` | + at least one Kivira-affiliated executive account |
| Daily connection-request capacity | ~25 / day | ~50-75 / day combined |
| Active campaigns supported simultaneously | 3 (one sender stretched thin) | 3-5 (per-sender campaign assignment) |
| Weekly accept production (at current rates) | ~10-15 / week | ~30-50 / week |

## Candidate senders (tradeoffs each)

### Option A: Kivira founder (Maria T Carmona)

- **Pro:** highest credibility surface; founder-from-founder DMs land harder on healthcare-system / payer recipients.
- **Pro:** aligns with the v5 message pattern's *"Demo would be with our founder"* beat — recipients already know who they're hearing from.
- **Con:** founder's LinkedIn is a strategic asset; sending volume from it dilutes its quality if outbound replies are poor.
- **Con:** founder's time on inbox triage is expensive.
- **Recommended use:** dedicated to the highest-value tiers only (3A / 3B / 3C) at lower volume (~15/day cap, not 25). Strategic, not scale.

### Option B: Dedicated outbound account (new LinkedIn)

- **Pro:** infinitely scalable; no risk to existing executive profiles.
- **Pro:** can be branded as a Kivira BD / GTM role title.
- **Con:** brand new accounts have low connection-request acceptance and require weeks of warm-up (real activity: posts, connection-accepts, comments) before being effective.
- **Con:** HeyReach treats new accounts cautiously; warm-up sequences run at lower volume initially (~5-10/day for first 2 weeks).
- **Recommended use:** start the warm-up now in parallel so it's ready as the second-volume lever by 2026-06.

### Option C: Kivira CTO or other named team member

- **Pro:** real human, real LinkedIn presence, credible role.
- **Pro:** no warm-up overhead — established account.
- **Con:** CTO outbound is off-mission; pulling them in dilutes their core function.
- **Con:** clinical / sales-facing personas may not respond as well to a technical title.
- **Recommended use:** technical-gatekeeper persona threads only (CMIO, CIO, VP Interoperability), if those become a focus. Not for general ramp.

### Option D: Kivira advisor or board member

- **Pro:** very high credibility, especially if they have public healthcare visibility (e.g., a medical board member).
- **Pro:** can be one-touch leveraged for warm intros without ongoing outbound burden.
- **Con:** advisors do not run cadenced outbound — this is a one-shot ask, not a ramp lever.
- **Recommended use:** see [[LINKEDIN_CONNECTION_EXPORT_AS_GTM_2026_05_12]] for the proper one-shot ask. Not a sender ramp candidate.

## Recommended week-of-2026-05-12 sequence

1. **Day 1-2:** Decide on the second sender. Default recommendation: Maria (Option A) for strategic tier-3 outreach.
2. **Day 1-2:** Provision a new dedicated outbound account (Option B) and begin warm-up. Set a 10-day timer; do not send outbound from it until 2026-05-22.
3. **Day 3:** Attach Maria's account to HeyReach. Run a small Wave 2 campaign through it — ~50-100 leads at the 3A / 3B health-system + IDN tier (the cohorts where Wave 1 had zero hits). Cap day-volume at 15/day, not 25.
4. **Day 4-5:** Verify per-sender campaign assignment is working (replies route to the correct sender's inbox; HeyReach's inbox view filters by `linkedInAccountId`).
5. **Day 5-7:** Wave 2 campaigns now run with 2 senders. Keegan handles 1A / 1C / 2C; Maria handles 3A / 3B / 3C.

## Anti-pattern: don't ramp before list tightens

Wave 1's 17% in-scope ratio was list-driven, not message-driven (see [[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]]). Adding senders to Wave 1's noisy list would simply scale the 83% noise rate. Order matters:

1. First: tighten list filters at the Clay-enrichment step.
2. Then: confirm the in-scope ratio crosses 30% on a small Wave 2 pilot.
3. Then: ramp senders.

Skipping straight to step 3 would invert the throughput-to-signal ratio. Do not.

## HeyReach mechanics (operational)

- Multiple LinkedIn accounts attach to a single HeyReach workspace via `/li_account/Add` (or the HeyReach UI). Each gets a unique `linkedInAccountId` that propagates through `/campaign/GetAll` → `campaignAccountIds`.
- Per-campaign sender assignment is configured at campaign creation. To shift an existing campaign's sender, the campaign must be paused → re-assigned → resumed (similar pattern to the `excludeInOtherCampaigns` toggle).
- Per-sender daily caps: default 25, configurable per campaign. Recommended starting point for a newly-attached executive account is **15/day for the first 5 days**, then ramp to 25/day if accept rates are normal.
- Inbox filtering: HeyReach's `/inbox/GetConversationsV2` returns conversations across all senders; filter client-side by `linkedInAccountId` to attribute replies to the right sender. (Verified during Wave 1 weekly-puller work.)

## Reputation guardrails

- **LinkedIn weekly invite cap:** the platform-wide ceiling is ~100 connection requests per account per *week* (historically ~25/day × 4 days, soft-enforced). Stay below this; HeyReach respects it but the cap is the cap.
- **Sender warm-up activity:** a new sender's account should post / comment / connect manually for 2 weeks before HeyReach outbound. Skipping warm-up triggers LinkedIn's anti-spam heuristics.
- **Reply rate as a health metric:** if any single sender's reply rate drops below 15% for a week, pause that sender's campaigns and investigate before ramping further.

## Refresh cadence

This plan covers the immediate (5/12-5/18) ramp. After the new sender(s) run for 2 weeks, evaluate against [[OUTREACH_BASELINE_METRICS]] Wave 2 actuals and mint a successor `OUTBOUND_SENDER_RAMP_<next-period>` if the targets need recalibration.
