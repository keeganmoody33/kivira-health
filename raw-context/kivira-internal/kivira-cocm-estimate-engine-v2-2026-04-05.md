---
source_path: "/Users/keeganmoody/Downloads/Kivira docs/kivira cocm estimate v2.pdf"
ingested_at: 2026-04-06
source_type: pdf
status: canonical-markdown-ingest
note: "Extracted with PDFKit into markdown summary. The PDF contains an embedded Python engine source file."
---

# Kivira Public Medicare CoCM Opportunity Estimate Engine v2.1

## Purpose

This PDF contains the reference Python engine for the public Medicare CoCM opportunity estimate workflow. It is explicitly framed as modeled, public-data-only output rather than audited truth.

## Validity notes in the source

- Uses public Medicare fee-for-service claims only.
- Excludes Medicare Advantage, commercial, Medicaid, and uninsured populations.
- Public CMS files may suppress values involving fewer than 11 beneficiaries.
- Provider-to-organization affiliation is estimated from public provider data and may be imperfect.
- Reported opportunity values are modeled estimates, not audited financial statements.
- CoCM beneficiary totals are an aggregate public proxy, not a deduplicated patient funnel.

## Reference interfaces

### CLI flags

- `--org-name`
- `--state`
- `--city`
- `--org-type`
- `--max-candidates`
- `--include-low-confidence`
- `--experimental-blended-denominator`
- `--output-dir`
- `--persona`
- `--json`
- `--csv`
- `--batch`

### Reference account profiles

The engine embeds an `ACCOUNT_PROFILES` list with examples such as:

- Banner Medical Group
- Aledade ACO NC
- Privia Health

Each account profile contains:

- `org_name`
- `state`
- `city`
- `org_type`
- `priority_personas`
- `max_candidates`
- `notes`

## Public data inputs

### NPPES

The engine resolves:

- organization identity from Type 2 NPPES lookups
- known aliases
- known cities
- known ZIPs
- identity quality (`weak`, `moderate`, `strong`)

It then searches Type 1 clinicians and filters to PCP taxonomies.

### CMS Part B

The engine pulls public Part B rows keyed by NPI and retains signals for:

- `G0444`
- `96127`
- `99492`
- `99493`
- `99494`
- `G2214`
- `99484`

## Modeling assumptions

### `solo_practice` and `independent_group`

- Conservative: rate `0.06`, payment `$110`, months `3`
- Base: rate `0.10`, payment `$120`, months `5`
- Aggressive: rate `0.15`, payment `$135`, months `7`

### `aco_parent`

- Conservative: rate `0.08`, payment `$115`, months `4`
- Base: rate `0.14`, payment `$130`, months `6`
- Aggressive: rate `0.20`, payment `$145`, months `8`

### `health_system_medical_group` default

- Conservative: rate `0.08`, payment `$115`, months `4`
- Base: rate `0.12`, payment `$127`, months `6`
- Aggressive: rate `0.18`, payment `$140`, months `8`

## Confidence-grade rules

The embedded engine scores:

- clinician match quality
- screening signal volume
- organization identity quality
- CoCM public visibility
- penalty for blended denominator use

### Thresholds

- `A >= 80`
- `B >= 55`
- `C >= 30`
- `D < 30`

### Match-quality contribution

- `>= 10` high-confidence clinicians: `+35`
- `>= 5` high-confidence clinicians: `+25`
- `>= 5` combined high + medium: `+15`
- `>= 3` total matches: `+5`

### Screening-volume contribution

- `G0444 >= 100`: `+25`
- `G0444 >= 50`: `+20`
- `G0444 >= 20`: `+12`
- `G0444 > 0`: `+5`

### Identity-quality contribution

- strong: `+20`
- moderate: `+10`

### CoCM visibility contribution

- reported: `+10`
- not reported or suppressed: `+5`

### Blended denominator penalty

- experimental blended denominator: `-10`

## Modeled output fields

The engine emits:

- matched clinicians
- high-confidence clinicians
- `g0444_benes`
- `96127_benes`
- `cocm_benes`
- `cocm_services`
- `cocm_revenue`
- conservative gap
- base gap
- aggressive gap
- confidence grade
- caveats
- persona messages

## Persona messages in the source

The engine contains templated messages for:

- `pcp`
- `medical_director`
- `cfo`
- `cmio`
- `pop_health`
- `bh_ops`

Those messages are already softened around causality and use modeled-public-data caveats rather than treating the gaps as audited truth.

## Export contract

### JSON

- org/state
- observed metrics
- modeled opportunity range
- confidence grade
- caveats
- persona messages

### One-row CSV

- org/state
- clinician counts
- observed metrics
- conservative/base/aggressive gap
- confidence grade

### Provider debug CSV

- NPI and provider identity
- affiliation score and confidence
- match reasons
- observed code-level public signals

## Implementation implication

This source is the architectural reference for the repo-local rebuild, but not the production code artifact. The repo-local version should keep its contracts and logic shape while replacing the PDF-embedded script with clean package code and synthetic-first fixtures.
