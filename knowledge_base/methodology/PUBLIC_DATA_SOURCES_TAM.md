---
name: PUBLIC_DATA_SOURCES_TAM
description: Free public data sources for Kivira TAM building - NPPES, CMS, HRSA, NCQA sources mapped to subtiers.
domain: methodology
node_type: framework
status: validated
last_updated: 2026-04-06
tags:
  - methodology
  - workflow
  - tam-total-addressable-market
  - source-research-synthesis
topics:
  - tam-total-addressable-market
  - workflow
  - gtm-motion
related_concepts:
  - "[[ACCOUNT_SCHEMA_EXTENDED]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[SUBTIER_EXCLUSION_RULES]]"
  - "[[TAM_DEDUP_METHODOLOGY]]"
  - "[[LIST_BUILD_ACCESSIBILITY_FIRST]]"
  - "[[OPERATIONAL_LIST_VS_STRATEGIC_TAM]]"
source:
  type: research-synthesis
  file: "raw-context/MARKETANALYSIS.md"
  date: "2026-04-06"
---

# Public Data Sources for TAM Building

Free public data stack for Kivira GTM list building without Definitive Healthcare.

[VERIFIED: URLs and field availability confirmed as of 2026-04-06]

## The Core Stack (Use These First)

NPPES + CMS Provider Data Catalog + HRSA + CMS MSSP/ACO REACH PUFs will get you 80% of the way for all tiers.

---

### 1. NPPES NPI Registry — Foundational Layer for All Tiers

**URL:** `download.cms.gov/nppes/NPI_Files.html`

**What it is:** Base list for every subtier. Covers every HIPAA-covered provider in the U.S.

**Key fields:**
- Type 1 NPI = individual clinician
- Type 2 NPI = organization/group practice
- Taxonomy codes for specialty filtering
- `authorized_official_*` fields = person who registered the org (often practice administrator or managing physician)

**Primary care taxonomy codes:**
- `207Q00000X` = Family Medicine
- `207R00000X` = Internal Medicine
- `207QA0505X` = Adult Medicine
- `363L00000X` = Nurse Practitioner (Primary Care)

**For Tier 1A and 1B:**
1. Pull all Type 2 NPIs with primary care taxonomy codes
2. Filter by `entity_type_code = 2` (organization)
3. Monthly bulk download is ~1GB ZIP, free

**What it gives you:** Org name, address, taxonomy, authorized official name/title, NPI

**What it doesn't give you:** Size, revenue, payer mix, EHR platform

---

### 2. CMS Provider Data Catalog — Doctors and Clinicians National File

**URL:** `data.cms.gov/provider-data/dataset/mj5m-pzi6`

**What it is:** CMS Care Compare underlying dataset.

**Key field:** `group practice PAC ID` — clusters individual clinicians into group practice entities

**For Tier 1A and 1B:**
1. Count how many PCPs are in each group
2. This gives you a rough size filter for Tier 1A floor (≥5 PCPs) and Tier 1B floor (≥3 PCPs)
3. Join to NPPES on NPI to enrich Type 2 records with clinician headcounts per org

**This is the closest free substitute for Definitive Healthcare's "clinician count per group" field.**

---

### 3. CMS MSSP ACO Participant File — Tier 1C and Tier 2A

**URL:** `data.cms.gov/medicare-shared-savings-program/accountable-care-organization-participants`

**What it is:** 480 ACOs participated in MSSP in 2024, covering 14.3M Medicare beneficiaries as of January 2026.

**Key fields:**
- ACO name, TIN, primary contact
- ACO type (Track, ENHANCED, etc.)
- Service area (counties/states)
- Assigned beneficiary count
- Participating provider TINs (join back to NPPES)

**For Tier 1C:**
1. Download participant-level file
2. Filter to provider groups (non-hospital TINs with PCP taxonomy dominance)
3. These are your VBC provider groups operating under shared savings — highest-priority Tier 1C accounts

---

### 4. CMS ACO REACH Participant List — Tier 1C and Tier 2A

**URL:** `cms.gov/priorities/innovation/files/aco-reach-py2026-participants.pdf`

**What it is:** 74 ACOs in PY 2026 (down from 103 in 2025, 122 in 2024 — model is consolidating around serious operators).

**Key fields:** ACO name, state, participant entity names, website

**These are your highest-pain Tier 2A accounts** (global capitation, downside risk).

**Cross-reference move:** Match ACO REACH participants against MSSP file to identify orgs participating in multiple risk models — these are your Tier 1C + Tier 2A dual-tag accounts.

---

### 5. HRSA Health Center Finder — Tier 1B (FQHC Track)

**URL:** `data.hrsa.gov/topics/health-centers`

**What it is:** Full downloadable list of all 16,200+ FQHC and Look-Alike sites as CSV/XLSX.

**Key fields:**
- Organization name, address, contact
- Awardee type (H80 grant recipient vs. Look-Alike)
- Patient population served
- Services offered (including behavioral health)
- Site count per grantee

**For Tier 1B FQHC filter:**
1. Set floor: grantees with ≥3 service delivery sites
2. Filter for behavioral health services listed
3. Grantees with behavioral health integration are pre-qualified Kivira fits

---

### 6. NCQA Behavioral Health Integration Distinction — Priority Signal

**URL:** `ncqa.org/programs/health-care-providers-practices/patient-centered-medical-home-pcmh/distinction-in-behavioral-health`

**What it is:** Searchable directory of PCMH-recognized practices with Behavioral Health Integration distinction.

**Why it matters:** These practices have formally committed to integrated BH workflows. This is your warmest Tier 1A/1B signal. They already believe the problem is real and have started building infrastructure. Pre-qualified clinical champions.

**Limitation:** Full directory is searchable but not bulk-downloadable for free. Scrape or manually compile by state.

**If `bhi_distinction = true`:** Set `outreach_priority: wave_1`

---

## Secondary Sources (Tier-Specific)

| Source | URL | Best For | What You Get |
|--------|-----|----------|--------------|
| CMS PECOS Enrollment File | `cms.gov/newsroom/fact-sheets/public-provider-and-supplier-enrollment-files` | All tiers | Medicare billing enrollment, org type, TIN → confirms active billing status |
| CMS Order & Referring File | `data.cms.gov/provider-characteristics/medicare-provider-supplier-enrollment/order-and-referring` | 1A, 1B | Individual PCPs actively billing Medicare; join to group PAC ID to size the group |
| HRSA Area Health Resources File (AHRF) | `data.hrsa.gov/data/download` | 1A, 1B geographic targeting | County-level PCP density, shortage areas, mental health workforce data — use for geo-prioritization |
| CarePrecise | `careprecise.com` | 1A, 1B | ~$300–500 one-time purchase; org + clinician + affiliation data derived from Medicare claims. Closest free-adjacent substitute for Definitive HC. |
| AHA Annual Survey (public summaries) | `aha.org` | 3A, 3B | Hospital system counts, employed physician totals, affiliation data |
| CMS Provider of Services (POS) File | `data.gov/dataset/provider-of-services-file` | 3A, 3B | Hospital and non-hospital facility certification, ownership, accreditation, location |

---

## How to Build the Tier 1A List Specifically

Since Tier 1A (mid-market provider groups) is the first outbound lane, here is the exact build sequence:

### Step 1 — NPPES pull
Download full monthly file. Filter:
- `entity_type_code = 2` (org)
- Primary care taxonomy codes
- `provider_business_practice_location_address_state_name` for your target states

### Step 2 — CMS Doctors & Clinicians join
Use `group PAC ID` field to count PCPs per org. Filter to orgs with ≥5 PCPs. This gets you to multi-site, operationally real organizations.

### Step 3 — MSSP participant cross-reference
Flag any Tier 1A org whose TIN appears in MSSP participant file. These get:
- `subtier_secondary_tags: ["1C_vbc", "2A_aco_affiliated"]`
- Elevated `pilot_feasibility_score`

### Step 4 — NCQA BHI flag
Check NCQA directory for any of your Tier 1A orgs. If they have BHI distinction:
- `bhi_distinction: true`
- `outreach_priority: wave_1`

### Step 5 — LinkedIn enrichment
Take filtered org list and run LinkedIn company search for each to pull five buying-committee roles using persona-title dictionary. This is where Clay or Apollo earns its keep — feed NPPES org name + state + NPI and let it match to LinkedIn company page.

### Step 6 — Apply exclusion rules
Single-site with <3 PCPs, purely FFS with no quality contract signal, no identifiable decision-maker → `outreach_priority: disqualified`

---

## Dedup Keys Across Sources

The deduplication schema holds because every account carries `parent_org_id` and `subtier_primary`:
- When you build Tier 1C next, any org already in Tier 1A list that shows up in MSSP file gets tagged secondary, not duplicated
- **NPI and TIN are your dedup keys across every source**

---

## Source Quality Tiers

| Quality | Sources | Use |
|---------|---------|-----|
| **Gold** | NPPES, CMS MSSP PUF, CMS ACO REACH | Canonical account identification |
| **Silver** | HRSA Health Centers, CMS Provider Data Catalog | Enrichment and sizing |
| **Bronze** | NCQA directories, AHA summaries | Signal and prioritization |
| **Paid-adjacent** | CarePrecise (~$300–500) | Best free-adjacent substitute for Definitive HC |

## Related Concepts

- [[ACCOUNT_SCHEMA_EXTENDED]] — Fields these sources populate
- [[GTM_TIER_ARCHITECTURE_9_SUBTIERS]] — Subtiers these sources map to
- [[SUBTIER_EXCLUSION_RULES]] — Rules to apply after sourcing
- [[TAM_DEDUP_METHODOLOGY]] — Dedup logic across sources
