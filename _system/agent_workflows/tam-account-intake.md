# TAM Account Intake

## Purpose

Normalize arbitrary TAM/list-building CSV inputs into the repo-local account schema before any scoring, routing, or brief generation.

## Inputs

- Raw CSV exports from spreadsheets, Apollo, Clay, or manual lists
- Source-system hint if known

## Required normalized fields

- `org_name`
- `state`
- `city`
- `org_type`
- `priority_personas`
- `max_candidates`

## Steps

1. Map arbitrary headers into canonical fields.
2. Normalize enum-like values such as `org_type`.
3. Parse comma- or pipe-delimited persona lists.
4. Fill defaults for missing-but-safe fields like `max_candidates`.
5. Preserve validation status and emit row-level errors instead of silently dropping context.

## Outputs

- normalized CSV
- validation errors CSV

## Guardrails

- Never invent `org_type` when source data is ambiguous; flag the row.
- Keep output schema superset-friendly so later stages can add modeled fields without changing the base contract.
