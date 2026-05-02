# Tiered Outreach Planner

## Purpose

Translate modeled opportunity and confidence into a tier, an outbound recommendation, and the correct sequencing logic.

## Inputs

- estimated account CSV

## Steps

1. Apply the deployment-guide tier thresholds.
2. Mark whether numeric claims are allowed.
3. Recommend direct outreach, discovery-first outreach, nurture, or no outbound.

## Outputs

- tiered CSV

## Guardrails

- Do not let Tier 3 or Tier 4 rows inherit Tier 1 style number-led copy.
- Keep tiering deterministic so spreadsheet and CLI results match.
