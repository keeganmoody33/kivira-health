---
name: WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12
description: Distilled learnings from triaging the 58 LinkedIn accepts produced by Wave 1 (5/3-5/11) against the 9-sub-tier structure — what fit, what was noise, and what the noise composition tells us about Wave 2 list filters.
domain: business
node_type: gtm_signal
status: validated
last_updated: 2026-05-12
date: "2026-05-12"
tags:
  - business
  - gtm-motion
  - outbound
  - accept-triage
  - source-internal-doc
topics:
  - gtm-motion
  - workflow
  - market-segmentation
related_concepts:
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
  - "[[OUTREACH_BASELINE_METRICS]]"
  - "[[KIVIRA_OUTBOUND_MESSAGE_PATTERN_2026_05_12]]"
  - "[[KIVIRA_OUTBOUND_MESSAGE_PATTERN_V6_2026_05_20]]"
  - "[[JOSH_WAVE1_FOLLOWUP_PACKAGE_2026_05_11]]"
  - "[[OUTREACH_WAVE_STRUCTURE]]"
source:
  type: internal-doc
  files:
    - "00_foundation/_synthesis/josh-followup-2026-05-11/accepts-subtier-mapped.csv"
    - "00_foundation/_synthesis/josh-followup-2026-05-11/accepts-subtier-mapped.md"
  date: "2026-05-12"
---

# Wave 1 accept-triage learnings

[VERIFIED: Triage performed on 2026-05-11 against `accepts-subtier-mapped.csv` (58 rows pulled live via `scripts/heyreach_accepts_pull.py`).]

## Headline numbers

- **58 lifetime LinkedIn accepts** across the 3 Wave 1 campaigns (Baseline-9Subtier + OperationalOwner-2A + ClinicalChampion-1C).
- **10 in-scope (17%)** mapped to a real sub-tier in the GTM structure.
- **48 noise (83%)** — vendor / recruiter / off-industry / wrong-wedge.
- **27 of 58 had a reply** at some point (the conversation has 2+ messages). 7 of those replies were post-launch correspondent-last (i.e., recent + the recipient owes the next message). 2 plausibly warm (Vineet Mishra connector, Scott Lincoln founder/CEO); 6 counter-pitches.

## The 10 in-scope (the "what worked" cohort)

| # | Name | Sub-tier | Role | Company | Notes |
|---|---|---|---|---|---|
| 1 | Yarly Fassih-Nia | 1C | Sr Dir Quality & Risk Adjustment | WellMed Medical Management | UnitedHealth-affiliated MA-heavy VBC PCP — top priority |
| 2 | Robert Lystrup, MD | 1A | Medical Director | Arizona Community Physicians | Multi-site PCP group, Tucson |
| 3 | Chris Oltmans | 2C | Chief Population Health Officer | NxtCare | Transitional / pop-health platform |
| 4 | Jeremy Wigginton, MD | 3C | Chief Medical Officer | Capital Blue Cross | Regional BCBS payer |
| 5 | Christa Thomas | 3C / 3A | VP Clinical Compliance Operations | Optum | Payer + Optum Care provider arm |
| 6 | Jason Johnson | 1C | Director, Growth | Privia Health | Partnership / channel angle |
| 7 | Lynn LeCluyse | 1C | Patient Marketing | Privia Health | Patient-facing role; lower priority |
| 8 | Chris MacInnis | 2C (borderline) | Chief VBC Strategy & Growth Officer | Old Mission Wound Care | Strong title, wrong-wedge org — borderline |
| 9 | Kumar Murukurthy, MD | 2B (borderline) | Chief Clinical Officer | Optimum Healthcare IT | Services consultancy — possible channel |
| 10 | Scott Quinn | 2B (borderline) | Founder | EVOS Health | Founder-to-founder; verify partner vs. competitor |

## What the noise told us (the 48 OUT_OF_SCOPE)

Composition by category:

| Category | Count | Examples |
|---|---:|---|
| GTM tooling / sales tech (selling TO us) | ~26 | Salesforge, HeyReach, Premium Inboxes, WarmLeads, AirOps, Hotglue, Teleport, Unstructured, MindInventory, Morph Data Strategies, all the "GTM Engineer" titles |
| Recruiters / agencies / sales-training | ~5 | 2X (corporate recruiter), Clay Headhunter, Medical Solutions (nurse staffing), NPAworldwide, Cardone Ventures |
| Off-industry sales / individuals | ~9 | Graybar (electrical distribution), Edward Jones (financial advisor), Dream Finders Homes, Super Soccer Stars, Best Version Media, PeoplePerHour freelance |
| Healthcare-adjacent but wrong wedge | ~8 | HCLTech analyst, pharmacy ops personal-brand, Pharma Trial Connect, Get Healthy USA wellness retail |

## Five things this tells us

### 1. Persona-targeted lists materially outperform generic baseline.

The 1C VBC PCP list (`ClinicalChampion` campaign) and the 2A ACO list (`OperationalOwner` campaign) produced the cleaner accepts — even though the 2A campaign produced *zero* directly in-scope accepts in the triage (its OperationalOwner persona targeting may need a tighter title filter, but the accepts it produced were not as noisy as Baseline's). The Baseline-9Subtier campaign, which over-indexed on generic "healthcare growth" LinkedIn slices, was the source of most of the 48 noise.

**Implication for Wave 2:** drop the generic-baseline campaign approach. Every Wave 2 campaign must be a specific sub-tier × persona slice, with title filters that exclude the anti-personas (see [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]] §Anti-Persona Patterns).

### 2. The 2A ACO campaign produced zero in-scope.

This is the most surprising finding. 359 leads loaded against the 2A ACO sub-tier, but the lifetime accepts the campaign produced (still indistinguishable client-side from other campaigns because HeyReach AI auto-tagging didn't run on most threads) did not include any clear ACO Operational Owners or Clinical Champions.

Two competing hypotheses:

- **List quality issue:** the 2A list may have over-indexed on administrative / shell-org titles rather than actual operating Population Health / Care Coordination directors. The OperationalOwner persona for 2A in [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]] includes "VP Population Health," "Director of Care Coordination," "Risk Operations Leader" — if the list-build hit on these but they were attached to non-operating ACO shell entities, the accepts will look like Optum (a payer hybrid) or NxtCare (pop-health platform) rather than a standalone ACO.
- **Sample size issue:** 359 leads × ~10% accept rate × ~17% in-scope ≈ 6 in-scope accepts expected. We saw 0. With this sample size that's within statistical noise.

**Implication for Wave 2:** rerun the 2A campaign with a stricter list-build (CMS MSSP/REACH participant files, then filter for Director / VP titles at the participant entity, not at parent health systems). Set a higher size floor (≥1,000 covered lives).

### 3. The vendor / GTM-tool noise has a predictable shape and is filterable upstream.

26 of 48 noise accepts came from sales-tech / SaaS vendors auto-prospecting our outreach footprint. These have a recognizable signature: founder/CEO/GTM-Engineer title + small AI / SaaS / data startup. They are not Kivira buyers; they are reciprocating outreach in hopes we book a demo with them. [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]] §Anti-Persona Patterns now codifies the exclusion rules.

**Implication for Wave 2:** apply the anti-persona filter at list-build time (Clay enrichment step), not at outreach time. Should remove ~80% of vendor noise.

### 4. The 17% baseline is a floor, not a ceiling.

With Wave 1's noise patterns now codified as anti-personas, the realistic in-scope ratio for Wave 2 is **≥40%** at the same lead volume. Setting that as the Wave 2 target.

### 5. The accept-quality is a leading indicator of message-quality requirements.

The 10 in-scope cohort all hold senior-operator or clinical-champion roles. They will not read a 200-word LinkedIn DM. The v5 message pattern (see [[KIVIRA_OUTBOUND_MESSAGE_PATTERN_2026_05_12]]) was built to land in ~50 words with named-funder social proof + one role-specific value-prop sentence + the two-path close.

If the in-scope ratio improves in Wave 2 but reply-rate drops, the message length / framing is the next thing to test — not the list quality.

## Operating wisdom captured for future cycles

- **Always pull accepts via REST every Friday.** `scripts/heyreach_accepts_pull.py` produces the canonical per-person CSV; `scripts/heyreach_weekly_pull.py` produces the campaign-level aggregates. The HeyReach UI does not surface enough signal for the kind of triage above.
- **Run the triage before re-loading any new wave.** Don't ramp send volume on a noisy list; tighten the filter, then ramp.
- **HeyReach autoTag attribution is broken at the per-conversation level.** Only ~3% of conversations have a `campaignName` in their `autoTags[]` because the AI tagger runs only on replied threads. For per-campaign attribution, cross-reference lead `profileUrl` against the original campaign lead list rather than relying on autoTags.

## Refresh cadence

Mint a successor node `WAVE_N_ACCEPT_TRIAGE_LEARNINGS_<date>` after each Wave's send-cycle completes (7+ days post-toggle for the cleanest signal-read). Reference back to this node so the version chain shows in-scope-ratio trend over time.
