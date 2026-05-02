# Claims-Safe Outbound

## Purpose

Generate discovery-safe, grade-aware outbound briefs that respect CDS framing and public-data caveats.

## Inputs

- routed and tiered account CSV

## Steps

1. Use org-type buyer context to set the lead angle.
2. Use confidence grade to decide whether numbers may appear.
3. Generate persona-specific brief text, likely objections, and discovery questions.
4. Keep the language inside Kivira's CDS and evidence guardrails.

## Outputs

- brief CSV
- optional per-account JSON brief artifacts

## Guardrails

- Grades `A/B` may include modeled range with caveats.
- Grade `C` must use the category story in written outbound.
- Grade `D` is qualify-first / do-not-outbound.
- Never drift into autonomous-diagnosis language.
