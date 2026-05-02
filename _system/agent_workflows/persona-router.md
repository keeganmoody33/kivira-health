# Persona Router

## Purpose

Convert `org_type` and priority persona inputs into a concrete buyer sequence and title map for outreach and CRM work.

## Inputs

- normalized or estimated account CSV

## Steps

1. Resolve the default persona order for each `org_type`.
2. Merge any account-specific `priority_personas` without losing the required default order.
3. Output both abstract persona tokens and real-world title variants.

## Outputs

- routed CSV with buyer sequence
- persona title map JSON per account

## Guardrails

- CMIO is a workflow/informatics champion, not a generic IT placeholder.
- For ACOs, population health is primary and finance is supporting unless the account demands otherwise.
