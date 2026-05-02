# Wave 1A Execution Schedule — HeyReach Sourcing

**For:** Josh Pappas
**From:** Keegan
**Date:** 2026-05-01
**Subtier:** 1A — Mid-Market Provider Groups (≥5 PCPs, ≥2 sites)
**Channel:** LinkedIn via HeyReach (sole channel for this wave)
**Tooling cost:** $0 incremental (HeyReach already provisioned)
**Geographic scope:** National, with optional GA + NC diagnostic subset (see Day 2)

---

## TL;DR

We have everything we need to run Wave 1A on HeyReach without buying Clay, Sales Nav, or Apollo. The full pipeline is documented at `_system/agent_workflows/heyreach-zero-budget-sourcing.md` and is built to be reused for the other 8 subtiers — we only do this design work once.

The schedule below is the first execution. Goal: **first connection requests sent on Day 4. First demo booked by Day 14.** The process gets faster on every subsequent subtier because we keep the artifacts and templates.

---

## Why This Order, In One Paragraph

We're pre-seed. Pilot acquisition is the overriding priority ([[PILOT_SITE_ACQUISITION_PRIORITY]]). 1A is the wedge per `PRIMARY_CARE_WEDGE_ICP` — multi-site primary care groups with mental health workload. Without paid enrichment, we use NPPES + CMS public data to build the qualified account universe, then Google X-ray search + LinkedIn's free company People tab to find the five personas per company. HeyReach handles the actual outreach. Operational Owner gets the first thread because they feel the workflow pain daily and are reachable on LinkedIn (per the buying-committee logic on the messaging board).

---

## Day-by-Day

### Day 1 (today, 2026-05-01) — Account Universe

**Output:** `fixtures/wave1a_raw_accounts.csv`

| Action | Owner | Time |
|--------|-------|------|
| Download NPPES monthly bulk file (~1GB ZIP) from `download.cms.gov/nppes` | Keegan | 30 min |
| Run `scripts/build_list_1a.py` against NPPES + CMS Doctors & Clinicians | Keegan | 30 min |
| Cross-reference MSSP participant file for `subtier_secondary_tags: ["1C_vbc"]` | Keegan | 20 min |
| Manually flag NCQA-BHI distinction practices (top 50 by state) | Keegan | 60 min |
| **Stage gate:** raw account count + state distribution review | Keegan | 15 min |

**Expected output volume:** 800-1,500 raw orgs nationally. The script's existing PCP taxonomy filter + ≥5 PCP floor does the bulk of the cut.

---

### Day 2 — Qualify + Geographic Slice Decision

**Output:** `fixtures/wave1a_qualified.csv`

| Action | Owner | Time |
|--------|-------|------|
| Apply `SUBTIER_EXCLUSION_RULES` (universal + 1A-specific) via `tam_builder/pilot_filters.py` | Keegan | 30 min |
| Score each remaining org: BHI distinction +2, MSSP +1, ≥3 sites +1 | Keegan | 30 min |
| **Decision point:** national vs. GA + NC slice. National = bigger surface, slower per-account work. GA + NC = tighter slice, faster Stage 3-4, easier follow-up if a call lands. | Keegan + Josh | 15 min |
| Sort qualified list descending by score; take top 100-150 for Wave 1A | Keegan | 20 min |

**Recommendation:** Run national for Stage 1+2 (cheap), then take the top-scoring 150 orgs nationally for Stage 3+4 (expensive). If GA + NC has ≥40 orgs in the top 150, we can run a parallel diagnostic slice without extra pipeline work.

---

### Day 3 — Resolve Company LinkedIn URLs

**Output:** `fixtures/wave1a_with_linkedin.csv`

| Action | Owner | Time |
|--------|-------|------|
| Google batch: `"<Org Name>" site:linkedin.com/company` for top 150 orgs | Keegan or scripted | 2-3 hrs |
| LinkedIn direct search fallback for non-hits (~30 orgs expected) | Keegan | 60 min |
| Mark `NOT_FOUND` for any org that fails both — these get re-queued for Wave 2 | Keegan | 15 min |

**Expected hit rate:** 75-85% for 1A. Mid-market provider groups have inconsistent LinkedIn presence. We accept this and move on.

---

### Day 4 — Find Personas (Operational Owner First)

**Output:** `fixtures/wave1a_persona_urls.csv` (Operational Owner column populated)

| Action | Owner | Time |
|--------|-------|------|
| Run Google X-ray for **2 priority Operational Owner title variants** per resolved company (see "Decision Needed" below) | Keegan | 3-4 hrs |
| LinkedIn Company People tab for top 30 highest-scored accounts (manual sweep) | Keegan | 90 min |
| Capture profile URL, name, title, confidence per row | Keegan | (during above) |
| Drop `confidence: low` rows from the HeyReach load file | Keegan | 10 min |

**Stage gate:** target 80-100 Operational Owner profile URLs at `confidence: high or medium`. If we land below 60, we adjust title variants and re-run.

---

### Day 5 — HeyReach Campaign A Launch (Operational Owner)

**Output:** Live HeyReach campaign sending connection requests

| Action | Owner | Time |
|--------|-------|------|
| Build HeyReach Campaign A with 5-step sequence (connect → thank → value → ask → breakup) | Keegan | 90 min |
| Pull message variants from `MESSAGING_HYPOTHESIS_DISCIPLINE` — Workflow/Ops primary theme | Keegan | 30 min |
| Load `wave1a_persona_urls.csv` (Operational Owner rows only) into HeyReach | Keegan | 15 min |
| Set daily cap: 25 connection requests/day | Keegan | 5 min |
| **Launch.** | Keegan | — |

**Volume math:** 80-100 contacts × 25/day = ~3-4 days to clear the connection-request queue. The sequence runs over ~18 days from first send to last breakup message.

---

### Day 6-7 — Personas 2 + 3 (Clinical Champion, Tech Gatekeeper)

**Output:** Persona URL CSV updated; Campaigns B + D loaded but not launched

| Action | Owner | Time |
|--------|-------|------|
| Repeat Stage 4 process for Clinical Champion (CMO, VP Medical Affairs, Medical Director variants) | Keegan | 3-4 hrs |
| Repeat for Tech Gatekeeper (CMIO, CIO, VP Clinical Informatics variants) | Keegan | 2-3 hrs |
| Build Campaigns B + D in HeyReach but **leave paused** | Keegan | 60 min |

**Why paused:** per `COCM_OUTREACH_SEQUENCING`, Clinical Champion goes second after the Operational Owner thread is warm or has responded. We launch Campaign B only after Operational Owner replies start landing (typically Day 8-10).

---

### Day 8-12 — Reply Triage + Campaign B Launch + Demo Booking

| Action | Owner | Time |
|--------|-------|------|
| Daily HeyReach inbox triage; tag replies by intent (interested / not now / wrong person / no) | Keegan | 30 min/day |
| When Operational Owner accept-rate ≥ 25%, launch Campaign B (Clinical Champion) | Keegan | 5 min |
| For interested replies, send Calendly link manually | Keegan | per reply |
| **First demo booking target: Day 12-14** | — | — |

---

### Day 13+ — Economic Buyer + BH Influencer (gated)

| Action | Trigger |
|--------|---------|
| Launch Campaign C (Economic Buyer / CFO/COO) | Only after at least one Operational Owner OR Clinical Champion thread is warm at the same company. **Do NOT cold-thread C-suite at health systems** (per "Do Not" rules on messaging board). |
| Launch Campaign E (BH/Quality Influencer) | Only when a demo is scheduled — they need to see the product to validate workflow fit. |

---

## Decision Needed (for Wave 1A — your domain call)

The Operational Owner persona has 7 title variants in our 1A table:

> Director of Operations · VP Operations · Director of Care Management · Population Health Director · Director of Clinical Programs · Director of Quality · VP Clinical Operations

For Day 4, we need to **pick the 2 we run X-ray queries for FIRST**. The trade-off:

- **Director of Care Management** + **Population Health Director** → narrowest, highest-fit clinical operators. Probably the truest pain-feelers. Lower hit rate because the title is less common at smaller groups.
- **Director of Operations** + **VP Operations** → broadest, easiest to find on LinkedIn. Less specific to BH workload pain. Higher false-positive rate (some are pure ops, not clinical).
- **Director of Quality** + **Director of Clinical Programs** → middle ground; aligns with quality/compliance secondary theme.

**Pick 2.** I'll seed the queries with your choice and we adjust on Day 4 if hit rate is poor. *This is the one decision in the schedule that nobody but you can make.*

---

## Risks + Mitigations

| Risk | Mitigation |
|------|-----------|
| Google rate-limits on X-ray queries | Spread across days; cap at 100 queries/day per IP; fall back to LinkedIn People tab |
| LinkedIn flags HeyReach activity | Daily cap at 25; full sequence pacing of 5+ days; no message blasts |
| Operational Owner persona is missing from many 1A orgs (small groups don't have a Pop Health Director) | Title-variant fallback chain — drop to "Office Manager" or "Practice Administrator" if 3+ priority titles fail per org |
| Replies pile up before Campaigns B-E launched | Manual reply handling first 7 days; only launch Campaign B once a clear cadence is set |
| <3 demos booked by Day 21 | Re-run messaging hypothesis cycle; pull Operational Owner sequence apart for theme A/B test |

---

## What's NOT in Scope This Wave

- Email outreach (waiting on sequencer + inbox infra decisions)
- Phone dialing (separate motion via office-manager track)
- CRM (Airtable Free will hold the wave1a CSVs; HeyReach is system of record for outreach state)
- Subtiers 1B-3C (process is now documented; runs in subsequent waves)

---

## Reusability — What Comes Out of Wave 1A

After Wave 1A completes, we have:

1. **A validated 5-stage zero-budget sourcing pipeline** (`heyreach-zero-budget-sourcing.md`)
2. **Hit-rate benchmarks** for Stage 3 and Stage 4 we can extrapolate to other subtiers
3. **Working HeyReach sequence templates** per persona that we tune, not rebuild
4. **A Stage 2 score function** in `tam_builder/pilot_filters.py` proven at 1A scale
5. **A reply-pattern map** showing which primary themes (Workflow/Ops, Clinical Outcomes, ROI) get the most engagement at the 1A persona × theme intersection

Wave 1B should take roughly half the calendar time of 1A. Wave 1C onward should take a third.

---

**Sources:**
- [Canonical sourcing process](computer:///Users/keeganmoody/KIVIRA.HEALTH/_system/agent_workflows/heyreach-zero-budget-sourcing.md)
- [Public data sources](computer:///Users/keeganmoody/KIVIRA.HEALTH/knowledge_base/methodology/PUBLIC_DATA_SOURCES_TAM.md)
- [Subtier exclusion rules](computer:///Users/keeganmoody/KIVIRA.HEALTH/knowledge_base/methodology/SUBTIER_EXCLUSION_RULES.md)
- [Outreach sequencing logic](computer:///Users/keeganmoody/KIVIRA.HEALTH/knowledge_base/methodology/COCM_OUTREACH_SEQUENCING.md)
- [Pilot site acquisition priority](computer:///Users/keeganmoody/KIVIRA.HEALTH/knowledge_base/methodology/PILOT_SITE_ACQUISITION_PRIORITY.md)
- [Existing 1A list builder script](computer:///Users/keeganmoody/KIVIRA.HEALTH/scripts/build_list_1a.py)
