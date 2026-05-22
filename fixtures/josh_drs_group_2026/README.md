# Josh Drs Group 2026 — HeyReach pilot fixtures

LinkedIn-first pilot list built from Josh CSV exports + existing wave1/ACO TAM fixtures.

## Source files (repo root)

- `Drs Group US_Kivira Project 2026 - READ.csv` — title playbook (not contacts)
- `Drs Group US_Kivira Project 2026 - Physician_Group_Nationwide_Execs_.csv` — ~161k headerless exec rows
- `Drs Group US_Kivira Project 2026 - Kivira Target PCP List_ April 2026.csv` — curated seed (~80 rows)

## Pipeline

```bash
python3 scripts/run_josh_pilot_pipeline.py
```

Stages write artifacts in this directory:

| File | Stage |
|------|--------|
| `josh_exec_normalized.csv` | ingest |
| `josh_pcp_seed.csv` | ingest |
| `read_title_buckets.yaml` | ingest |
| `candidates_filtered.csv` | filter |
| `candidates_with_subtier.csv` | merge |
| `pilot_finalists_pre_linkedin.csv` | score |
| `pilot_linkedin_master.csv` | enrich |
| `pilot_heyreach_ready.csv` | gate |
| `heyreach_import.csv` | export |
| `heyreach_import_profile_detail.csv` | export (review) |

## Apollo manual merge (optional)

Drop Apollo export at `apollo_enriched.csv` with columns including person name, org, and LinkedIn URL. Re-run enrich stage only:

```bash
python3 scripts/enrich_josh_pilot_linkedin.py
```

## Enrichment options

- Requires `SPIDER_API_KEY` in `.env.local` for URL discovery and profile scrape.
- `--skip-scrape` — use search snippets only (faster).
- `--max-rows N` — limit Spider calls during smoke tests.

## HeyReach handoff

Import `heyreach_import.csv` — **profileUrl only** (no email/phone). Hard gate: URL + headline + `has_profile_photo=true`.

**List loaded (2026-05-22):** `Josh Drs Group Pilot 2026-05-22` → HeyReach list id **686808** (216 unique URLs).

### Campaign wiring (v6 playbook, paused until go-live)

1. Playbook: `knowledge_base/methodology/KIVIRA_FIRST_TOUCH_LINKEDIN_PLAYBOOK.md`
2. UI: create **5 PAUSED** cluster campaigns; paste from `heyreach_first_touch_v6_templates.md`
3. Paste IDs `A`–`E` in `josh_campaign_ids.json`; dry-run `python3 scripts/wire_josh_heyreach_campaigns.py`
4. `--commit` then `go_live_approved` + `--go-live` only after Keegan approves

See `GO_LIVE_CHECKLIST.md`. (`heyreach_lane_copy.md` is deprecated.)

## Last pipeline run (2026-05-22)

- Filtered candidates: 6,658 org-deduped rows (from 161k exec + PCP seed)
- Finalists scored: 225 (up to 25 per subtier)
- HeyReach-ready after gate: **217** (8 rejected — missing URL/headline/photo)
- Subtiers in export: 8 of 9 (one thin after gate — review `pilot_linkedin_master.csv` `validation_flags`)
