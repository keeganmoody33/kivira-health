# Wave 1 LinkedIn Search Queries — Master Seed File

**Purpose:** The priority list of LinkedIn free-search Boolean queries we run to seed `wave1_linkedin_master.csv`. Each query is designed to return profiles whose **employer** plausibly fits one of the 9 subtiers AND whose **title** matches one of the 5 personas.

**Mode:** Market test. We are NOT pre-qualifying accounts before LinkedIn search. We capture URLs, then back-tag subtier from the captured profile's `current_company`.

**Constraints:** Free LinkedIn account only. No Sales Nav. Industry filter applied via LinkedIn UI (not Boolean), location US, sort by relevance.

---

## How to Run a Query

1. Paste the Boolean string into LinkedIn's main search bar.
2. Click **People** (top of results).
3. Apply UI filters: **Locations = United States**, **Industry = [as noted per query]**.
4. Scroll. Capture profile URLs into `wave1_linkedin_master.csv` with the `source_query` field set to this query's ID (e.g., `Q1`, `Q2`).
5. Tag persona (per the title), then `subtier_guess` (per the company name → eyeball which of the 9 subtiers it most likely is).
6. Set `subtier_confidence`: `high` if the company name unambiguously matches a subtier (e.g., "Aledade" → 1C clear), `medium` if it's a fit but ambiguous (e.g., "ABC Medical Group" — could be 1A or 1B), `low` if you're guessing.

`low` rows DO NOT load into HeyReach. Park them for re-tag later.

---

## Wave 1A — Subtier 1A only (Mid-Market Provider Groups)

**Global note (demo / feedback):** The live pipeline can mix **all nine subtiers**; these queries intentionally bias toward **Tier 1 (1A–1C) and Tier 2 (2A–2C)**. Tier 3 (3A–3C) is not the focus for early calls but may appear in results—handle in HeyReach using `subtier` and campaign pacing.

**Goal (this section only):** Seed ~150–200 URLs → **80–100** viable rows after Parallel + `refine_subtier_1a()` (employer must confirm `1A`, high confidence when tagging Wave 1A–narrow loads).

**States:** Georgia OR North Carolina OR Tennessee OR South Carolina (paste into LinkedIn **Locations** UI).

**Industry (UI filter):** Prefer `Medical Practice` for pure groups; `Hospital & Health Care` only when pairing with strong group keywords below—expect extra triage.

**Group-intent keywords** (use in Boolean AND clauses): `medical group`, `physicians`, `physician group`, `IPA`, `clinically integrated network`, `multi-specialty`, `primary care`.

Parallel export JSON naming: save each query output as `fixtures/wave1_runs/<timestamp>/Q1A-N_raw_urls.json` with top-level `query_id` set to `Q1A-1` … `Q1A-5` (must match filename prefix so `parallel_persona_extractor.py` picks them up).

### Q1A-1 — Operational Owner (Tier 1A title dictionary)

- **Cluster:** OO-1 + OO-2 (`Director of Operations`, `VP Operations`, care management, population health).
- **Boolean:**
  ```
  ("Director of Operations" OR "VP Operations" OR "Director of Care Management" OR "Population Health Director" OR "Director of Clinical Programs" OR "VP Clinical Operations")
  AND ("medical group" OR "physicians" OR "IPA" OR "primary care")
  ```
- **Locations:** GA, NC, TN, SC (United States)
- **Industry:** `Medical Practice` (default)
- **Expected subtier:** `1A` primary; eyeball company → exclude systems/payers per subtier quick reference below.

### Q1A-2 — Clinical Champion

- **Boolean:**
  ```
  ("Chief Medical Officer" OR "CMO" OR "VP Medical Affairs" OR "Primary Care Medical Director" OR "Associate Medical Director")
  AND ("medical group" OR "physician" OR "IPA" OR "primary care")
  ```
- **Locations:** GA, NC, TN, SC
- **Industry:** `Medical Practice`

### Q1A-3 — Economic Buyer (narrow — avoids VP-of-HR noise)

- **Boolean:**
  ```
  ("Chief Financial Officer" OR "CFO" OR "Chief Operating Officer" OR "COO" OR "Managing Partner" OR "Executive Director")
  AND ("medical group" OR "physicians" OR "health partners")
  ```
- **Locations:** GA, NC, TN, SC
- **Industry:** `Medical Practice`
- **Note:** Do **not** rely on bare `"President"` searches—too noisy; keyword rules now exclude `Vice President` → president false positives in code.

### Q1A-4 — Technical Gatekeeper

- **Boolean:**
  ```
  ("CMIO" OR "Chief Medical Information Officer" OR "Director of Health IT" OR "EHR Administrator" OR "Director of Clinical Informatics" OR "VP Health IT")
  AND ("medical group" OR "physicians" OR "Epic" OR "Athena")
  ```
- **Locations:** GA, NC, TN, SC
- **Industry:** `Medical Practice` or `Hospital & Health Care` (if volume low—expect triage)

### Q1A-5 — BH / Quality Influencer

- **Boolean:**
  ```
  ("Director of Behavioral Health" OR "VP Behavioral Health" OR "Behavioral Health Program Director" OR "Director of Quality Improvement" OR "Director of Clinical Quality")
  AND ("primary care" OR "medical group" OR "integrated behavioral health")
  ```
- **Locations:** GA, NC, TN, SC
- **Industry:** `Medical Practice`

**HeyReach copy:** Paste messaging from [`00_foundation/messaging/wave1a_heyreach_copy.md`](../00_foundation/messaging/wave1a_heyreach_copy.md).

---

## Persona → Title Cluster Cheat Sheet

These 12 title clusters cover ~80% of the title variants across all 9 subtiers. Use them in your Boolean strings.

| Cluster ID | Persona | Title Variants (use any combination in OR) |
|------------|---------|--------------------------------------------|
| **OO-1** | Operational Owner | "VP Population Health" · "Director of Population Health" · "Director of Care Management" |
| **OO-2** | Operational Owner | "VP Care Transformation" · "Director of Care Transformation" · "Director of Clinical Programs" |
| **OO-3** | Operational Owner | "Practice Administrator" · "Practice Manager" · "Director of Practice Operations" |
| **CC-1** | Clinical Champion | "Chief Medical Officer" · "CMO" · "VP Medical Affairs" |
| **CC-2** | Clinical Champion | "Medical Director Population Health" · "Population Health Medical Director" · "Medical Director Value-Based Care" |
| **CC-3** | Clinical Champion | "Behavioral Health Medical Director" · "Chief Behavioral Health Officer" · "Behavioral Health Service Line Medical Director" |
| **EB-1** | Economic Buyer | "Chief Financial Officer" · "CFO" · "VP Finance" |
| **EB-2** | Economic Buyer | "Chief Operating Officer" · "COO" · "VP Operations" |
| **EB-3** | Economic Buyer | "VP Stars Performance" · "VP Medical Management" · "SVP Health Plan Operations" |
| **TG-1** | Tech Gatekeeper | "Chief Medical Information Officer" · "CMIO" · "VP Clinical Informatics" |
| **TG-2** | Tech Gatekeeper | "VP Data & Analytics" · "Director of Clinical Analytics" · "Director of Data Science" |
| **BH-1** | BH/Quality Influencer | "Director of Behavioral Health" · "VP Behavioral Health" · "BH Program Director" |

---

## Priority Queries (TODO — Keegan to write)

This is the only thing in this whole pipeline only YOU can decide. The order you run these queries in determines what fills the master CSV first, which determines what HeyReach campaigns we launch first, which determines what positioning we test first.

**Pick 5-8 queries** ordered by priority. For each:
- Cluster ID(s) being targeted
- LinkedIn Boolean string (will paste directly into search bar)
- Industry filter to apply in UI (one of: `Hospital & Health Care`, `Medical Practice`, `Mental Health Care`, `Hospitals and Health Care`, `Health, Wellness & Fitness`, `Insurance`, `Pharmaceuticals`)
- Optional location narrowing (US-wide default; optional state/metro)
- Subtier(s) you expect this to hit
- Why you put it in this slot

**Trade-offs to think about:**
- Broader queries (e.g., just `"CMO"` + Hospital industry) return more profiles but more noise — you'll spend more triage time.
- Narrow queries (e.g., `"VP Population Health" AND ACO`) return fewer profiles but higher fit — fewer to triage but smaller pool.
- Queries that hit 4+ subtiers at once (CMO, CFO) are efficient but we lose the ability to A/B which subtier responds.
- Queries that hit only 1-2 subtiers (Practice Administrator → 1A/1B only) tell us cleaner signal but cover less ground.
- Behavioral health-flavored queries (BH-1, CC-3) are typically warmest because the persona has self-selected into the problem we solve.

### Q1 — WORKED EXAMPLE (overwrite if you want)
- **Cluster:** `OO-1` + `OO-2` (Operational Owner — population health + care transformation flavors)
- **Boolean:** `("VP Population Health" OR "Director of Population Health" OR "Director of Care Management" OR "Director of Care Transformation") AND ("primary care" OR "ambulatory" OR "value-based")`
- **Industry filter:** `Hospital & Health Care` (apply via LinkedIn UI after running Boolean)
- **Location:** `United States`
- **Expected subtiers:** `1A, 1C, 3A, 3B` — wide net across provider org types where pop health roles concentrate
- **Why first:** Highest density of operators feeling daily mental-health-in-primary-care pain. The persona that converts internally per [[COCM_OUTREACH_SEQUENCING]]. Captures 4 subtiers in one query, so a single afternoon of triage seeds 4 HeyReach campaigns.

*Q2-Q8 below — overwrite Q1 if you'd rather lead differently.*

### Q2 — CLAUDE DRAFT (overwrite as needed)
- **Cluster:** `BH-1` (BH/Quality Influencer — behavioral health director flavor)
- **Boolean:** `("Director of Behavioral Health" OR "VP Behavioral Health" OR "Behavioral Health Program Director" OR "Director of BH Integration") AND ("primary care" OR "integrated care" OR "collaborative care")`
- **Industry filter:** `Hospital & Health Care`
- **Location:** `United States`
- **Expected subtiers:** `1A, 1B, 1C, 2C, 3A` — BH leaders concentrate at provider orgs
- **Why this slot:** Warmest persona. Self-selected into our problem. They feel BH workload pain in primary care daily and have personal credibility on the topic. Highest predicted reply rate.

### Q3 — CLAUDE DRAFT (overwrite as needed)
- **Cluster:** `CC-2` (Clinical Champion — population health / value-based flavor)
- **Boolean:** `("Medical Director Population Health" OR "Medical Director Value-Based Care" OR "Medical Director Quality" OR "Medical Director Primary Care") AND ("ACO" OR "value-based" OR "population health" OR "MSSP")`
- **Industry filter:** `Hospital & Health Care`
- **Location:** `United States`
- **Expected subtiers:** `1A, 1C, 2A, 3A, 3B` — clinical leaders at orgs with risk contracts
- **Why this slot:** Clinical credibility carriers at value-based orgs. They own the "is this clinically safe and outcomes-positive" question. CDS framing per [[CDS_NOT_DIAGNOSIS_FRAMING]] resonates here.

### Q4 — CLAUDE DRAFT (overwrite as needed)
- **Cluster:** `OO-3` (Operational Owner — practice administration flavor)
- **Boolean:** `("Practice Administrator" OR "Practice Manager" OR "Director of Practice Operations" OR "Director of Clinical Operations") AND ("primary care" OR "family medicine" OR "internal medicine" OR "PCMH")`
- **Industry filter:** `Medical Practice`
- **Location:** `United States`
- **Expected subtiers:** `1A, 1B` — sweet spot for the office-manager pilot motion
- **Why this slot:** Per [[THIRTY_DAY_OFFICE_MANAGER_TARGET]], office-manager-tier operators are the 30-day call target. Their LinkedIn presence is thinner than execs but the conversion-to-pilot path is shortest. Different industry filter (`Medical Practice`) catches groups not in the bigger systems Q1 hits.

### Q5 — CLAUDE DRAFT (overwrite as needed)
- **Cluster:** `TG-1` (Tech Gatekeeper — CMIO / clinical informatics flavor)
- **Boolean:** `("CMIO" OR "Chief Medical Information Officer" OR "VP Clinical Informatics" OR "Director of Clinical Informatics" OR "VP Health IT") AND ("primary care" OR "ambulatory" OR "EHR" OR "FHIR" OR "Epic")`
- **Industry filter:** `Hospital & Health Care`
- **Location:** `United States`
- **Expected subtiers:** `3A, 3B, 1C, 2A` — CMIOs sit higher up the org chart
- **Why this slot:** Per `COCM_OUTREACH_SEQUENCING`, tech gatekeeper runs in parallel with operator. We pre-warm them so when an operational owner says yes-to-pilot, we don't lose 6 weeks at security review. Lower volume but high strategic value.

### Q6 (optional — Claude suggestion if you want broader nets)
- **Cluster:** `OO-1 + OO-2` mid-market focus — same as Q1 but narrowed to provider groups via Industry filter `Medical Practice`. Catches 1A/1B operators that Q1 (Hospital & Health Care filter) misses.

### Q7 (optional)
- TODO — yours to write or leave blank

### Q8 (optional)
- TODO — yours to write or leave blank

---

**Note from Claude:** Q2-Q6 are first-swing drafts. The trade-off I made: weight toward personas with self-selected problem awareness (BH leaders, pop health operators) over balanced persona coverage. Reasoning: pre-seed pilot acquisition mode means reply rate beats buying-committee completeness. Overwrite anything that conflicts with your read of which orgs/personas are most reachable.

---

## After You Write Q1-Q8

I'll:
1. Sanity-check each Boolean for LinkedIn syntax (parens balanced, quotes correct, no banned operators).
2. Estimate result-count expectations per query so you know how much triage time to budget.
3. Lock the daily-cap math for HeyReach against the cumulative URL pool.
4. Build the per-persona HeyReach campaign templates that your captured URLs will feed into.

---

## Subtier Tag Quick Reference (for back-tagging in `subtier_guess`)

| Subtier | Heuristic Tell from Company Name |
|---------|----------------------------------|
| 1A | Multi-clinic group like "ABC Medical Group" / "XYZ Health Partners" — name suggests 5+ PCPs, multi-site |
| 1B | Single-name clinic / FQHC / federally-qualified language / "Family Practice" |
| 1C | Aledade-style brand · "ACO" in name · "Value-Based Care" in name · explicit MSSP/REACH mention on profile |
| 2A | "ACO" as the primary org name · "Medicare ACO" · "Accountable Care Organization" |
| 2B | Platform/SaaS naming · words like "enablement," "platform," "solutions" · employee count usually 50-500 |
| 2C | Care management / care coordination companies · names like "Vida," "Pearl," "Iris," "Wellth" |
| 3A | Brand names of regional health systems (Wellstar, Atrium, Northside, etc.) |
| 3B | Multi-state IDNs (HCA, Ascension, CommonSpirit, AdventHealth, etc.) |
| 3C | BCBS affiliates, Humana, Centene, Molina, regional Medicaid MCOs |

---

**Created:** 2026-05-01
**Owner:** Keegan
**Next step:** Fill Q1-Q8 above, then ping me to seed the queries.
