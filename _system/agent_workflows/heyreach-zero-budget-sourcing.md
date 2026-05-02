# HeyReach Zero-Budget LinkedIn Sourcing — Canonical Process

**Purpose:** Take a qualified subtier account list and produce a CSV of LinkedIn profile URLs for the five buying-committee personas, ready to load into HeyReach. **Zero paid tools required.**

**Status:** Canonical. Reusable across all 9 subtiers. First validated on Wave 1A.

**Related:** [[GTM_TIER_ARCHITECTURE_9_SUBTIERS]] · [[PUBLIC_DATA_SOURCES_TAM]] · [[SUBTIER_EXCLUSION_RULES]] · [[COCM_OUTREACH_SEQUENCING]] · [[PERSONA_ROUTER]]

---

## Constraint Set

- **No paid enrichment** — no Clay, no Sales Navigator, no LinkedIn Premium, no ZoomInfo.
- **HeyReach is the only outreach tool**, and it accepts a CSV of LinkedIn profile URLs as input (no Sales Nav search URL required).
- **The only contact data needed is the LinkedIn profile URL** — no email, no phone.
- Apollo free trial (300 credits) is a *bonus* lookup channel, not the spine.

---

## Two Lanes

There are two ways to run this pipeline. Pick based on the goal of the wave.

### Fast Lane — Market Test Mode (people-first)

When the goal is **"see what positioning gets a response"** and we don't yet have signal on which subtier is most receptive. Skip account universe construction. Use LinkedIn free-tier Boolean search by title + industry filter to surface candidates across multiple subtiers in parallel. Tag each captured profile with a `subtier_guess` based on the visible employer.

- **Single master CSV:** `fixtures/wave1_linkedin_master.csv` (people-first, all subtiers, all personas)
- **Query seed file:** `fixtures/wave1_linkedin_queries.md` (priority Boolean queries, persona-tagged)
- **Expected speed:** First HeyReach upload within ~24 hours of writing the queries.

Use this lane for: Wave 1 (market test), or any wave where speed > precision.

### Methodical Lane — Account-First (qualified universe → personas)

When the goal is **"thoroughly cover one subtier with high confidence"** and we have time + a clear hypothesis to test. Build account universe from public data, qualify with exclusion rules, then resolve LinkedIn for personas at each qualified account.

- **Per-subtier CSVs:** `fixtures/wave_<N>_<subtier>_raw_accounts.csv` → `_qualified.csv` → `_with_linkedin.csv` → `_persona_urls.csv`
- **Expected speed:** 4-7 days per subtier from raw account pull to HeyReach load.

Use this lane for: Wave 2+ once we know which subtier(s) responded to Wave 1, or when running a thorough sweep of a single high-priority subtier.

---

## The Methodical-Lane Pipeline (Five Stages)

```
[1] Account universe       →   [2] Qualify        →   [3] Resolve company URL
    NPPES + CMS PUFs            apply exclusion         Google + LinkedIn
                                rules + score           Co. search

       →   [4] Find personas       →   [5] HeyReach load
            Google X-ray +              CSV import,
            LinkedIn Co. People         persona-tagged
            tab + Apollo (bonus)        sequences
```

Each stage outputs a CSV the next stage consumes. Every artifact lives in `fixtures/wave_<N>_<subtier>/` so re-runs are reproducible.

---

## Stage 1 — Account Universe (Public Data)

**Input:** subtier definition (e.g., 1A = mid-market provider groups, ≥5 PCPs, ≥2 sites).

**Sources** (from [[PUBLIC_DATA_SOURCES_TAM]]):

| Subtier | Primary source | Secondary | Tertiary |
|---------|----------------|-----------|----------|
| 1A | NPPES Type 2 + PCP taxonomy | CMS Provider Data Catalog (PAC ID for clinician count) | NCQA BHI directory |
| 1B | NPPES Type 2 + PCP taxonomy + HRSA Health Centers | CMS Order & Referring | NCQA PCMH directory |
| 1C | CMS MSSP participant file + ACO REACH | NPPES (PCP taxonomy filter) | — |
| 2A | CMS MSSP / ACO REACH parent entities | — | — |
| 2B | Crunchbase free + LinkedIn company search | Press releases via Google | — |
| 2C | Crunchbase free + LinkedIn company search | — | — |
| 3A | CMS POS file + AHA public summaries | NPPES Type 2 (hospital affiliations) | — |
| 3B | AHA IDN summaries + Definitive substitutes | CMS POS | — |
| 3C | NAIC payer directory + state DOI lists | CMS MA/MAPD plan data | — |

**Tool:** `scripts/build_list_1a.py` already exists for 1A. Clone its pattern for other subtiers.

**Output:** `fixtures/wave_<N>_<subtier>_raw_accounts.csv` — 1 row per organization with `org_name`, `state`, `metro`, `org_type`, source IDs.

---

## Stage 2 — Qualify (Exclusion + Score)

**Apply** [[SUBTIER_EXCLUSION_RULES]] to drop disqualified rows. Universal exclusions cut 20-40% off the top (solo practitioners, telehealth-only, closed entities). Subtier-specific size/payer floors cut the rest.

**Score** with the persona/pilot-fit fields already in `tam_builder/pilot_filters.py`:
- BHI distinction → +signal
- Multi-site → +signal
- VBC contract participation → +signal
- Active competitor signal → flag, don't exclude

**Output:** `fixtures/wave_<N>_<subtier>_qualified.csv` — typically 30-60% of raw input. This is the list you'll spend LinkedIn-resolution effort on.

**Why this matters:** Stage 3 is the slowest stage (manual + Google rate-limited). Cutting unqualified accounts before resolution saves hours per wave.

---

## Stage 3 — Resolve Company LinkedIn URL

For each qualified org, find its LinkedIn company page URL.

**Tactics, in priority order:**

1. **Google search:** `"<Org Name>" site:linkedin.com/company` — top result is almost always correct. Free, scriptable, ~100 queries per IP per day before captcha.
2. **Direct LinkedIn search:** type org name into LinkedIn's company search. Works when logged in, no Sales Nav required.
3. **NPI Registry → website → LinkedIn footer:** for orgs that don't surface in Google's LinkedIn index, find their website via NPPES address + Google, then check the website footer for LinkedIn link.
4. **Apollo free trial (bonus):** Apollo's company DB will return LinkedIn URLs for orgs it knows about. Use only for orgs that fail tactics 1-3 to conserve the 300 credits.
5. **Mark `linkedin_company_url: NOT_FOUND`** if all four fail. Don't waste cycles.

**Output:** `fixtures/wave_<N>_<subtier>_with_linkedin.csv` — adds `linkedin_company_url` column. Expected hit rate: 70-85% for 1A/1B (smaller orgs with weaker LinkedIn presence), 90%+ for 3A/3B (large systems are well-indexed).

**Time budget:** 1-2 minutes per org if done manually with a browser. Faster if you batch the Google queries through a script.

---

## Stage 4 — Find the Five Personas Per Company

This is the high-leverage stage. Use the title-variant tables (subtier 3A/3B/3C/2A/2B/2C/1A/1B/1C — the matrix on your messaging board) as the search dictionary.

**Per company, run two channels in parallel:**

### Channel A — Google X-ray (free, primary)

Template:
```
site:linkedin.com/in "<TITLE_VARIANT>" "<COMPANY_NAME>"
```

For each company × persona, run 2-3 of the highest-priority title variants. **Don't run all 7** — diminishing returns and you'll hit Google's rate limit faster. Per `COCM_OUTREACH_SEQUENCING`, prioritize:
- Operational Owner first (most variants, most hits — start broad)
- Clinical Champion second
- Economic Buyer third (CFO/COO — typically findable)
- Tech Gatekeeper fourth (CMIO/CIO/VP IT — often well-indexed)
- BH/Quality Influencer last (often missing on LinkedIn — accept lower hit rate)

Capture: profile URL, name, title, persona tag, company.

**Tip:** Append `-recruiter` or `-jobs` to filter out recruiters poaching for similar roles. Append a second company synonym (`"<Company>" OR "<Company> Health"`) to catch profile listings using brand variants.

### Channel B — LinkedIn Company People Tab (free, supplementary)

Open the LinkedIn company page → People tab → filter by "Job title contains: <variant>." LinkedIn shows ~10-25 profiles before asking you to upgrade — that's enough to catch the obvious ones Google missed.

This works *without* Sales Nav. It's slower (manual per company) so reserve for top-priority accounts (BHI distinction, multi-site, etc.).

### Channel C — Apollo (bonus, gated)

If Apollo free trial credits remain, use only for orgs where Channels A+B returned <2 personas total. Apollo's people search returns LinkedIn URL + title for free-tier accounts.

**Output:** `fixtures/wave_<N>_<subtier>_persona_urls.csv` with columns:
```
org_name, linkedin_company_url, persona, persona_priority,
contact_name, contact_title, linkedin_profile_url, source_channel, confidence
```

**Confidence** = `high` if exact title match + correct company, `medium` if title in same family + correct company, `low` if uncertain (do not load to HeyReach as `low`).

---

## Stage 5 — HeyReach Load

HeyReach accepts a CSV of LinkedIn profile URLs. Build **one campaign per persona type** so the message variant matches the recipient (per [[COCM_OUTREACH_SEQUENCING]]):

- Campaign A: Operational Owner — Workflow/Ops primary message
- Campaign B: Clinical Champion — Clinical Outcomes primary message
- Campaign C: Economic Buyer — ROI/Revenue primary message (only after a thread is warm — DO NOT lead cold)
- Campaign D: Tech Gatekeeper — Technical/Integration primary message
- Campaign E: BH/Quality Influencer — Quality/Compliance primary message (load at demo stage)

**Sequence shape per HeyReach campaign:**
1. Connection request with one-line note (no pitch)
2. Day +2: thank-you message (still no pitch)
3. Day +5: value message tied to the persona's primary theme
4. Day +10: soft ask for 15-min discovery
5. Day +18: breakup message ("if not the right person, who is?")

**Daily volume cap:** 25-30 connection requests/day per LinkedIn account on HeyReach Growth ($79/mo, 1 sender seat). Going higher trips LinkedIn's spam detection.

**Tagging:** Every record carries `subtier`, `persona`, `account_score`, `wave` so reply-rate analysis can cut by any dimension.

---

## Re-Run Protocol (Apply After Each Subtier)

After each subtier wave runs, capture:

1. **Stage 3 hit rate** (% of qualified orgs with resolved LinkedIn URL)
2. **Stage 4 hit rate per persona** (which personas are gettable from public search, which aren't)
3. **HeyReach connection acceptance rate per persona × subtier**
4. **Reply rate per persona × primary message theme**

These four numbers tell you whether the next subtier's effort budget should rebalance: spend more on Stage 3 (if URLs are missing), spend more on Stage 4 channels (if personas are missing), or rewrite messaging (if accept-but-no-reply).

---

## What This Process Does NOT Do

- **No email sourcing.** That's a separate channel and waits until you commit to a sequencer + LeadMagic.
- **No phone enrichment.** Office-manager dialing is a separate motion.
- **No automated outreach beyond HeyReach.** Email warmup, multi-domain rotation, deliverability — out of scope until the wishlist tools are procured.
- **No CRM ingestion.** Airtable Free can hold the qualified account list, but tracking sits on HeyReach + a manual reply log until a CRM is chosen.

---

## Sources

- [[PUBLIC_DATA_SOURCES_TAM]] — public data origin for Stage 1
- [[SUBTIER_EXCLUSION_RULES]] — Stage 2 filter logic
- [[COCM_OUTREACH_SEQUENCING]] — sequencing logic for Stage 5
- [[PERSONA_ROUTER]] — title-variant dictionary in `tam_builder/constants.py`
- `scripts/build_list_1a.py` — reference implementation for Stage 1 + 2

---

**Created:** 2026-05-01
**Status:** Active. To be re-validated after Wave 1A run.
