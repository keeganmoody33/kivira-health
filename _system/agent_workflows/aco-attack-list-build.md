# ACO attack list build (2A)

**Canonical script:** `scripts/build_aco_attack_lists.py`  
**Policy node:** `knowledge_base/methodology/ACO_ATTACK_MOTION_2A_PRIMARY.md`

## When to run

- Before an ACO blitz block ([[ACO_BLITZ_2026_05_W2_PLAN]])
- Before loading Wave 2 LinkedIn 2A ([[OUTREACH_WAVE_STRUCTURE]])
- After refreshing CMS MSSP Organizations or ACO REACH participant files

## Command

```bash
python3 scripts/build_aco_attack_lists.py
```

Optional:

```bash
python3 scripts/build_aco_attack_lists.py \
  --reach-csv artifacts/aco_reach_py2026.csv \
  --wave2-size 135 \
  --blitz-size 40
```

## Outputs (`fixtures/aco_attack/`)

| File | Purpose |
|------|---------|
| `mssp_2a_master.csv` | All net 2A orgs after shell/hospital exclusions |
| `high_fit_2a.csv` | HIGH fit: `enhanced_track=1` and `agreement_period_num>=3`, or REACH |
| `wave2_linkedin_2a.csv` | Top 135 high-fit orgs for Spider / HeyReach account spine |
| `blitz_focus_2a.csv` | 40 orgs for sync email+phone; CMS exec required; excludes Wave 1 HeyReach 2A pool by default |
| `excluded_2a.csv` | Audit trail for excluded rows |

## CMS source

- **MSSP Organizations (PY2026):** `https://data.cms.gov/sites/default/files/2026-04/358ddf60-c203-41ef-a0c6-a62a79f466ee/PY2026_Medicare_Shared_Savings_Program_Organizations.csv`
- Cached locally: `artifacts/cms_mssp_orgs_py2026.csv` on first run

## Persona LinkedIn load (after Spider)

```bash
python3 scripts/build_aco_persona_heyreach.py \
  --aco fixtures/wave1_runs/<run>/Q2A_ACO_raw_urls.json \
  --bh  fixtures/wave1_runs/<run>/Q2A_BH_raw_urls.json \
  --out-heyreach fixtures/heyreach_loads/heyreach_leads_2a_persona_v2.json \
  --out-meta fixtures/aco_persona_ranked_v2.csv \
  --apply-anti-persona
```

Anti-persona and unknown-title drops use `tam_builder/aco_persona_rules.py` (aligned with [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]).

## Do not

- Use CMS placeholder title `ACO Executive (per CMS public filing)` as the LinkedIn persona target — blitz uses CMS exec; LinkedIn uses Spider-matched pop-health titles only.
- Double-touch blitz accounts on LinkedIn (see blitz plan channel specs).
