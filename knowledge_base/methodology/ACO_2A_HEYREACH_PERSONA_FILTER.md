---
name: ACO_2A_HEYREACH_PERSONA_FILTER
description: List-build rules for Tier 2A LinkedIn/HeyReach — anti-persona exclusion, persona buckets from title+snippet, and ban on CMS placeholder exec titles as operating buyers.
domain: methodology
node_type: pattern
status: emergent
last_updated: 2026-05-21
tags:
  - methodology
  - gtm-motion
  - outbound
  - workflow
topics:
  - gtm-motion
  - outbound
  - workflow
  - market-segmentation
related_concepts:
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
  - "[[ACO_ATTACK_MOTION_2A_PRIMARY]]"
  - "[[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]]"
  - "[[OUTBOUND_TWO_CHANNEL_POSTURE_2026_05_12]]"
  - "[[CMS_MSSP_ORGANIZATIONS_PY2026_2A_LIST_SPINE]]"
source:
  type: notes
  file: "Cursor session ACO placement and TAM plan implementation 2026-05-21"
  date: "2026-05-21"
---

# ACO 2A HeyReach persona filter (2026-05-21)

[VERIFIED: Drop counts from `scripts/build_aco_persona_heyreach.py --apply-anti-persona` on 20260521 Spider runs.]

## Problem

Wave 1 loaded **359** OperationalOwner-2A leads and produced **zero** in-scope accepts. Contributing factors:

1. **Pain anchoring** — 1A-style visit copy on network-level 2A buyers ([[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]).
2. **List noise** — generic “healthcare growth” and vendor/recruiter titles ([[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]] §Anti-Persona).
3. **Wrong contact role** — CMS public filing uses placeholder title `ACO Executive (per CMS public filing)`; that is a **blitz** contact, not a LinkedIn persona target.

## Canonical implementation

| Layer | Location |
|-------|----------|
| Persona regex + anti-persona | `tam_builder/aco_persona_rules.py` |
| Spider merge + tier A/B/C | `scripts/build_aco_persona_heyreach.py` |
| BH-purpose ranking (snippet) | `scripts/build_aco_bh_purpose_list.py` |

**HeyReach load flag:**

```bash
python3 scripts/build_aco_persona_heyreach.py \
  --aco fixtures/wave1_runs/20260521T191019Z/Q2A_ACO_raw_urls.json \
  --bh  fixtures/wave1_runs/20260521T163822Z/Q2A_BH_raw_urls.json \
  --out-heyreach fixtures/heyreach_loads/heyreach_leads_2a_persona_v2.json \
  --out-meta fixtures/aco_persona_ranked_v2.csv \
  --apply-anti-persona
```

## Filter rules

1. **Anti-persona** — recruiter, SDR, GTM engineer, vendor tools, etc. (dictionary §Anti-Persona).
2. **Unknown persona** — title+snippet matches no 2A bucket → drop from HeyReach JSON (keep in metadata CSV as Tier C / audit).
3. **Tier C org collision** — brand token is US state name only → metadata only, not HeyReach.
4. **CMS placeholder** — do not treat `ACO Executive (per CMS public filing)` as Operational Owner for LinkedIn; use Spider-matched pop-health / quality / BH titles.

## 2026-05-21 calibration run

| Metric | Value |
|--------|------:|
| Spider URLs in | 607 |
| After anti-persona + unknown drop | 433 |
| HeyReach JSON (Tier A+B) | **408** |
| Unique ACO orgs | 196 |
| Persona mix (top) | op_owner 200, clin_champ 107, econ_buyer 104 |

[INFERRED: Still async-channel test; sync blitz uses [[CMS_MSSP_ORGANIZATIONS_PY2026_2A_LIST_SPINE]] exec fields, not this JSON.]

## Channel split (do not double-touch)

| Channel | Contact source |
|---------|----------------|
| Sync blitz | `fixtures/aco_attack/blitz_focus_2a.csv` — `exec_*` CMS fields |
| LinkedIn Wave 2 | `heyreach_leads_2a_persona_v2.json` — Spider persona hits |

See [[OUTBOUND_TWO_CHANNEL_POSTURE_2026_05_12]] and [[ACO_BLITZ_2026_05_W2_PLAN]].

## Related Concepts

- [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]] — Tier 2A title Boolean strings
- [[ACO_ATTACK_MOTION_2A_PRIMARY]] — 2A primary entity motion
- [[WAVE_1_ACCEPT_TRIAGE_LEARNINGS_2026_05_12]] — Wave 1 accept/noise evidence
