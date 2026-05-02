---
name: tam-account-intake
description: Normalize TAM/list-building CSV inputs into the repo-local account schema before scoring or routing.
model: inherit
---

# TAM Account Intake

Use the canonical workflow spec at `_system/agent_workflows/tam-account-intake.md`.

## Required behavior

- Normalize arbitrary CSV headers into the canonical account schema.
- Preserve validation errors instead of silently discarding rows.
- Keep the output compatible with the repo-local TAM builder CLI.
