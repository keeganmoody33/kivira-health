---
name: INBOXKIT_SENDKIT_SEQUENCER_ROADMAP
description: Target operating model for outbound—InboxKit fully configured for domains/mailboxes/warmup; SendKit (sendkit.ai) as the locked sequencing layer pending vendor call and integration work.
domain: methodology
node_type: framework
status: emergent
last_updated: 2026-05-04
tags:
  - methodology
  - gtm-motion
  - source-public-web
  - gtm-tooling
topics:
  - outbound-infrastructure
  - deliverability
related_concepts:
  - "[[TECH_STACK_OUTBOUND_INFRASTRUCTURE]]"
  - "[[OUTREACH_BASELINE_METRICS]]"
  - "[[COCM_OUTREACH_SEQUENCING]]"
  - "[[LIST_BUILDING_STACK_CLAY_ENRICHMENT]]"
  - "[[CANONICAL_GTM_SEGMENTATION_MIRO_BOARD]]"
source:
  type: hybrid
  references:
    - url: "https://sendkit.ai"
      note: "Public vendor positioning — email sequencing, dedicated IPs, warmup, campaigns."
      date: "2026-05-04"
    - file: "raw-context/kivira-internal/kivira-gtm-tech-stack-executive-summary-2026-04-06.md"
      note: "Prior stack synthesis; update when SendKit decision is finalized."
---

# InboxKit + SendKit sequencer roadmap

## Target state (operator intent)

1. **InboxKit** — **fully configured** for workspace, domains, mailboxes, and warmup monitoring (REST/MCP patterns already documented under `knowledge_base/gtm_signals/inboxkit/` and `scripts/inboxkit_api_smoke.sh`).
2. **SendKit** — **lock the sequencer** on **[SendKit](https://sendkit.ai)** for campaign building, sends, and reply workflows so downstream analytics move from “Low Activity” / pre-sequencer states to live volume attributed to named campaigns.

[INFERRED: Division of labor — InboxKit as mailbox + reputation layer, SendKit as sequencing + execution UI — confirm contracts, DNS/auth handoffs, and whether HeyReach or another orchestrator remains source of truth for LinkedIn vs email.]

## Public reference (SendKit)

[VERIFIED: From vendor marketing site 2026-05-04 — **SendKit** advertises cold email sequencing, isolated/dedicated IP infrastructure, unlimited warmup on plans, campaigns/leads/analytics, and self-serve setup within minutes; pricing tiers listed publicly.]

Use this only for **external positioning** until procurement drops exact SKUs and data flows into `raw-context/kivira-internal/`.

## Next actions (checklist)

| Step | Owner | Done when |
|------|--------|-----------|
| Vendor call — SendKit | Ops/GTM | SSO, workspace model, mailbox import from InboxKit (or SMTP), and billing owner documented |
| Finish InboxKit hardening | Ops | All domains green per KPI, MCP wired where required, runbook updated |
| Campaign pilot | GTM | First sequence live in SendKit with named cohort + weekly evidence node |
| Update tech stack ingest | Ops | Add SendKit row to internal executive summary + link here |

## Evidence and API hygiene

- **InboxKit API:** use `POST /v1/api/mailboxes/list` and `scripts/inboxkit_api_smoke.sh` — not ad-hoc 404 paths (see repo `.cursorrules`).
- Do **not** commit API keys; store credentials per [[TECH_STACK_OUTBOUND_INFRASTRUCTURE]] ownership (Josh + Keegan).

## Related

- Latest operational snapshot: see weekly nodes under `knowledge_base/gtm_signals/inboxkit/` (e.g. warmup and UI captures).
- [[TECH_STACK_OUTBOUND_INFRASTRUCTURE]] — canonical stack narrative and internal file pointers.
- [[CANONICAL_GTM_SEGMENTATION_MIRO_BOARD]] — who we sequence against (segments and roles).
