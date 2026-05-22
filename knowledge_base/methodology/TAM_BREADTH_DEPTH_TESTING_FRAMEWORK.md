---
name: TAM_BREADTH_DEPTH_TESTING_FRAMEWORK
description: Stratified breadth-first TAM testing — one persona × one message per subtier, ~7% sample with holdout, prune/graduate thresholds, then depth on winners.
domain: methodology
node_type: framework
status: emergent
last_updated: 2026-05-22
tags:
  - methodology
  - gtm-motion
  - tam-total-addressable-market
  - outbound
  - metrics
topics:
  - gtm-motion
  - tam-total-addressable-market
  - workflow
  - execution-cadence
related_concepts:
  - "[[OUTREACH_BASELINE_METRICS]]"
  - "[[OUTREACH_WAVE_STRUCTURE]]"
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[MESSAGING_HYPOTHESIS_DISCIPLINE]]"
  - "[[WAVE_1_SCORING_FRAMEWORK]]"
  - "[[OUTBOUND_INBOX_SEND_VOLUME_MATH]]"
source:
  type: notes
  file: "cursor-session outbound-volume-planning 2026-05-22"
  date: "2026-05-22"
---

# TAM breadth vs depth testing framework

How to **test the full TAM for signal across subtiers** without burning the list before finding what works. Breadth eliminates clear losers; depth crowns winners.

[INFERRED: Sample sizes are directional at 150–300 contacts/cell (~3–9 replies at 1–3% reply rate); treat breadth wave as elimination, not statistical proof.]

## The dimensionality problem

Full combinatorial grid: **9 subtiers × 5 personas × 3 message themes = 135 cells** — untestable at pre-seed send capacity (~4,600 contacts/mo per [[OUTBOUND_INBOX_SEND_VOLUME_MATH]]).

**Collapse to 9 cells for breadth wave:** one priority-1 persona × one message hypothesis per subtier ([[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]).

## Breadth wave design

| Parameter | Value |
|-----------|-------|
| Cells | 9 (one per subtier) |
| Sample per cell | ~150–300 contacts |
| Total breadth sample | ~1,430 contacts |
| TAM holdout | ~93% (~16,410 cold contacts) |
| Sends (3-touch) | ~4,300 — fits one month moderate capacity |
| Active parallel sequences | Max 9 |

### Example persona picks (breadth wave)

| Subtier | Persona to test | Message theme (hypothesis) |
|---------|-----------------|---------------------------|
| 1A | Operational Owner | Workflow burden + BH gap |
| 1B | Practice Administrator / Office Manager | Time-back + CoCM revenue |
| 1C | VP Population Health | CMS V28 + risk-adjusted revenue |
| 2A | VP Population Health (ACO) | ACO quality + shared savings |
| 2B | VP Partnerships | Channel/embed (not direct sale) |
| 2C | VP Clinical Operations | BH workflow integration |
| 3A | VP Ambulatory | Ambulatory throughput + outcomes |
| 3B | VP Care Transformation | Enterprise BH integration |
| 3C | VP Medical Management / VP Stars | HEDIS + Stars |

## Signal thresholds (set before launch)

| Signal | Threshold (per cell) | Action |
|--------|---------------------|--------|
| Reply rate | <1% | Prune subtier OR change one variable (persona *or* message, not both) |
| Reply rate | 1–3% | Hold; iterate message |
| Reply rate | >3% | Graduate to depth wave |
| Positive replies | >0.5% | Graduate regardless of headline reply rate |
| Demos booked | ≥1 | Graduate immediately |

[UNVERIFIABLE: Industry ~2% cold reply baseline cited in [[OUTREACH_BASELINE_METRICS]] — validate externally before using as target.]

## 90-day arc

| Days | Activity | Cumulative TAM touched |
|------|----------|------------------------|
| 1–14 | Warmup + list build | 0% cold |
| 15–30 | Breadth wave (~1,430 contacts) | ~7% |
| 31–45 | Score; prune dead cells | — |
| 31–60 | Depth wave 1 — 2–3 winning subtiers, 2nd persona | ~16% |
| 61–90 | Depth wave 2 — wide inside winners, economic-buyer threads | ~30% |

After 90 days: **~70% of cold TAM held in reserve** for scaling into proven subtiers.

## Guardrails

1. **One variable at a time** per failing cell — otherwise attribution is unknowable.
2. **No multi-channel noise in breadth wave** — add LinkedIn/phone only on subtiers that pass threshold ([[OUTBOUND_TWO_CHANNEL_POSTURE_2026_05_12]]).
3. **Tag every send:** `(subtier, persona, message_variant, wave_id)` per [[OUTREACH_BASELINE_METRICS]].
4. **Control holdout:** ~50 contacts/subtier never touched until later (protects highest-fit accounts from bad first message).
5. **List quality before volume:** [[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]] — tighten Clay filters before breadth wave, not after.

## Key insight

> Use the breadth wave to **eliminate clear losers**, not to crown winners. Winners get crowned in the depth wave at ~1,000+ contacts in a single subtier × persona × message cell.

## Related concepts

- [[OUTREACH_WAVE_STRUCTURE]] — Wave 1–3 timing; breadth wave aligns with Wave 1 launch window
- [[MESSAGING_HYPOTHESIS_DISCIPLINE]] — all breadth messages are hypotheses until reply data validates
- [[GTM_30_60_90_EXECUTION_CADENCE]] — Day 30–60 measurement phase maps to breadth → depth transition
