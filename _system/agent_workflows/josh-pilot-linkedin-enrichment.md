# Josh pilot LinkedIn enrichment

Canonical workflow for enriching `pilot_finalists_pre_linkedin.csv` → `pilot_linkedin_master.csv`.

## Waterfall

1. Existing URL from wave1 fixture merge or valid Josh `col4_misc` (`linkedin.com/in`)
2. Optional `fixtures/josh_drs_group_2026/apollo_enriched.csv` (manual Apollo trial export)
3. Spider `/search` — `"{name}" "{org}"` (see `scripts/spider_query_runner.py`)
4. Spider `/scrape` on profile URL — headline, about, profile-photo heuristic
5. Parallel Search — fallback only (cap calls); not wired in batch script by default

## Required export fields

- `linkedin_profile_url`
- `linkedin_headline`
- `linkedin_position`
- `linkedin_about` (optional but ranked)
- `has_profile_photo` (hard gate for HeyReach export)

## Commands

```bash
python3 scripts/enrich_josh_pilot_linkedin.py
python3 scripts/enrich_josh_pilot_linkedin.py --skip-scrape --max-rows 20
```

## Claims

Outbound notes must follow `_system/agent_workflows/claims-safe-outbound.md` — CDS framing, no guaranteed revenue.
