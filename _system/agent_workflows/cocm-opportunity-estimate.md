# CoCM Opportunity Estimate

## Purpose

Estimate conservative/base/aggressive CoCM opportunity from normalized account inputs using the PDF-derived reference logic, while keeping the workflow synthetic-first and API-ready.

## Inputs

- normalized account CSV
- optional provider-debug fixture CSV
- adapter choice: `synthetic` today, `live-public` later

## Steps

1. Load org-type-specific modeling assumptions.
2. Read or synthesize observed public-signal fields.
3. Compute modeled conservative/base/aggressive gaps.
4. Compute confidence grade from match quality, screening signal, identity quality, and CoCM visibility.
5. Emit account-level contract files and provider-level debug output.

## Outputs

- combined estimates CSV
- per-account JSON summary
- per-account one-row summary CSV
- per-account provider debug CSV

## Guardrails

- Public-signal caveats must always travel with the estimate.
- Synthetic mode must preserve the same contract shape as future live mode.
