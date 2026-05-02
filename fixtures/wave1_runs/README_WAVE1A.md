# Wave 1A run directories

After running the five LinkedIn queries in [`wave1_linkedin_queries.md`](../wave1_linkedin_queries.md) (section **Wave 1A**), save Parallel / Spider JSON exports under a new timestamp folder:

```
fixtures/wave1_runs/<ISO_TIMESTAMP>/
  Q1A-1_raw_urls.json
  Q1A-2_raw_urls.json
  Q1A-3_raw_urls.json
  Q1A-4_raw_urls.json
  Q1A-5_raw_urls.json
```

Each file must follow the same JSON shape as existing `Q1_raw_urls.json` samples (`query_id`, `results[]` with `linkedin_profile_url`, etc.).

Then:

```bash
python scripts/parallel_persona_extractor.py --latest --processor base
```

Requires `PARALLEL_API_KEY` in `.env.local`. `--dry-run` validates wiring without API calls.
