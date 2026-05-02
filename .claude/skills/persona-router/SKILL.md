---
name: persona-router
description: Route accounts to the right buyer sequence and title map by org type.
model: inherit
---

# Persona Router

Use the canonical workflow spec at `_system/agent_workflows/persona-router.md`.

## Required behavior

- Route by `org_type` first.
- Output both persona tokens and real-world title variants.
- Keep CMIO, CIO, and CISO distinctions straight.
