# Manual Live-Public Smoke Path

The v1 CLI is synthetic-first by design. The `live-public` adapter name exists only to preserve the contract boundary for future CMS/NPPES work.

## Manual smoke checklist for a future live mode

1. Normalize a target account list into the canonical schema.
2. Implement a `LivePublicSignalAdapter` that resolves Type 2 organization identity, Type 1 clinician matches, and CMS Part B code-level public signals.
3. Run:

```bash
python3 scripts/kivira_tam_builder.py estimate-cocm \
  --input fixtures/normalized_accounts.csv \
  --output /tmp/live_estimates.csv \
  --artifact-dir /tmp/live_artifacts \
  --adapter live-public
```

4. Compare per-account JSON, summary CSV, and provider debug CSV against the synthetic contract shape before any GTM use.
