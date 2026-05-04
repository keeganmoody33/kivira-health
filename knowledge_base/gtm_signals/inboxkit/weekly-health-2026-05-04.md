---
name: WEEKLY_INBOXKIT_HEALTH_2026_05_04
description: InboxKit mailbox and warmup status for 2026-05-04 (product UI screenshots + MCP config note; REST API appendix)
domain: business
node_type: gtm_signal
status: emergent
date: "2026-05-04"
evidence_date: 2026-05-04
tags:
  - inboxkit
  - weekly-evidence
  - email-deliverability
topics:
  - outbound
related_concepts:
  - "[[TECH_STACK_OUTBOUND_INFRASTRUCTURE]]"
  - "[[OUTREACH_BASELINE_METRICS]]"
  - "[[OUTREACH_WAVE_STRUCTURE]]"
  - "[[WAVE_1_SCORING_FRAMEWORK]]"
source:
  type: screenshot_capture
  system: inboxkit # product UI + REST appendix; template: source inboxkit
  date: "2026-05-04"
  files:
    - raw-context/kivira-internal/inboxkit-ui-2026-05-04/mcp-settings.png
    - raw-context/kivira-internal/inboxkit-ui-2026-05-04/workspace-provisioning-overview.png
    - raw-context/kivira-internal/inboxkit-ui-2026-05-04/mailbox-health-table.png
related_sources:
  - type: api_snapshot
    note: Responses from `/v1/api/domains/list`, `/v1/api/mailboxes/list`, `/v1/api/warmup/list` via bearer API key + `scripts/inboxkit_api_smoke.sh`; useful for registrar-level domain rows versus dashboard KPI semantics
    date: "2026-05-04"
---

# InboxKit Health — May 4

Domain rollup pulled 2026-05-04 (UI KPIs + mailbox grid + REST cross-check — see screenshots in `raw-context/kivira-internal/inboxkit-ui-2026-05-04/` and Appendix A/B below).

| Domain | Mailboxes | Warmup Day | Health Score | Status |
|--------|-----------|------------|--------------|--------|
| groundskeep.xyz | 0 | — | — | registered; no mailboxes |
| kivira.online | 3 | 8 | ~98.4 | active; warmup in_progress |
| kivira.xyz | 3 | 8 | ~98.4 | active; warmup in_progress |
| kivirahealth.info | 2 | 8 | ~98.4 | active; warmup in_progress |
| kivirahealth.live | 2 | 8 | ~98.4 | active; warmup in_progress |
| kivirahealth.online | 3 | 8 | ~98.4 | active; warmup in_progress |
| kivirahealth.xyz | 3 | 8 | ~98.4 | active; warmup in_progress |
| scuttlewutt.com | 0 | — | — | registered; no mailboxes |

[VERIFIED: Operator-captured **InboxKit product UI screenshots** archived under `raw-context/kivira-internal/inboxkit-ui-2026-05-04/` on 2026-05-04.]

**Session note:** MCP in this Cursor project was not wired to **`https://mcp.inboxkit.com/mcp`** (OAuth-backed; no REST key needed for MCP). This node relies on captured UI metrics instead of calling InboxKit MCP tools in-chat.

## MCP connectivity (OAuth, no REST key required)

Captured from Settings → MCP in-product (see `raw-context/kivira-internal/inboxkit-ui-2026-05-04/mcp-settings.png`):

```json
{
  "mcpServers": {
    "inboxkit": {
      "url": "https://mcp.inboxkit.com/mcp"
    }
  }
}
```

First launch opens browser OAuth. Product copy lists intents such as global mailbox health, warmup status rollups, DNS checks, inbox placement runs, bounce filtering, etc.

## Provisioned inbox summary (dashboard KPI strip)

Per workspace overview screenshot (`workspace-provisioning-overview.png`):

| KPI (UI) | Value |
|----------|-------|
| Active Domains | 6 |
| Total Mailboxes | 16 |
| Active Mailboxes | 16 |

[VERIFIED: Product UI KPI row captured 2026-05-04 (local screenshot timestamps align with workspace assets).]

In-product narrative also flags warmup progress bars near **complete (~98%)** on the surveyed mailboxes and recommends **Configure the sequencer** as the next outbound step.

[INFERRED: “**Active Domains (6)**” is narrower than Registrar/API domain inventory that can include registered domains **without mailbox assignment**.] Cross-check Appendix A.

Representative mailbox rows listed in-product (six domains surfaced in provisioning view):

- `kivirahealth.{info,live,xyz}`
- `kivirahealth.online`
- `kivira.online`, `kivira.xyz`

## Mailbox analytics view (seven-day totals)

Captured `mailbox-health-table.png`. [VERIFIED: Table below transcribed verbatim from screenshot row labels and displayed metrics.]

Health column reads **Low Activity** (amber) for all enumerated mailboxes. **Bounce Rate** reads **0.0%** for every row.

| Mailbox | Health Status | Sent (7d) | Received (7d) | Reply Rate | Bounce Rate |
|---------|---------------|-----------|-----------------|------------|-------------|
| k_moody@kivirahealth.live | Low Activity | 3 | 2 | 0.0% | 0.0% |
| keegan@kivirahealth.live | Low Activity | 3 | 0 | 0.0% | 0.0% |
| keegan@kivirahealth.info | Low Activity | 3 | 2 | 0.0% | 0.0% |
| keegan.moody@kivirahealth.info | Low Activity | 5 | 2 | 40.0% | 0.0% |
| keegan.moody@kivirahealth.xyz | Low Activity | 4 | 2 | 0.0% | 0.0% |
| keegan@kivirahealth.xyz | Low Activity | 4 | 1 | 0.0% | 0.0% |
| keegan@kivira.online | Low Activity | 5 | 1 | 20.0% | 0.0% |
| keegan.moody@kivira.xyz | Low Activity | 2 | 1 | 0.0% | 0.0% |
| keegan@kivira.xyz | Low Activity | 4 | 1 | 25.0% | 0.0% |
| k_moody@kivirahealth.online | Low Activity | 6 | 2 | 33.3% | 0.0% |
| keegan.moody@kivirahealth.online | Low Activity | 2 | 0 | 0.0% | 0.0% |
| keegan@kivirahealth.online | Low Activity | 2 | 1 | 0.0% | 0.0% |
| k_moody@kivirahealth.xyz | Low Activity | 3 | 1 | 0.0% | 0.0% |
| k_moody@kivira.xyz | Low Activity | 3 | 0 | 0.0% | 0.0% |
| k_moody@kivira.online | Low Activity | 4 | 1 | 25.0% | 0.0% |
| keegan.moody@kivira.online | Low Activity | 3 | 1 | 0.0% | 0.0% |

Mailbox counts grouped by apex domain (**16**):

| Apex domain | Mailboxes |
|-------------|-----------|
| kivirahealth.online | 3 |
| kivirahealth.xyz | 3 |
| kivira.xyz | 4 |
| kivira.online | 2 |
| kivirahealth.info | 2 |
| kivirahealth.live | 2 |

## Interpretation

- **Provisioning / warmup UX:** KPI view shows sixteen live mailboxes and near-complete warmup visuals (~98% per provisioning screenshot), broadly consistent with `warmup_day` **8** and `health_score` **~98** from the ancillary REST warmup payload (Appendix B).

- **Engagement telemetry:** Mailbox analytics flags **Low Activity** for every sender while sequencer setup is pending — prioritize sequencer wiring rather than interpreting Low Activity alone as an infra outage.

- **Integrity:** Reply-rate variance (roughly **0–40%** column range) aligns with warmup-style synthetic engagement; reconcile after sequencer-backed production cadence ramps.

## Appendix A — REST domain registry sweep (cross-check only)

Eight domain rows existed in Registrar/API pull with **groundskeep.xyz** / **scuttlewutt.com** showing zero mailboxes. That explains why the UI KPI can read **six** active domains versus eight registrar-visible rows.

| Domain | Mailboxes (REST) |
|--------|------------------|
| groundskeep.xyz | 0 |
| kivira.online | 3 |
| kivira.xyz | 3 |
| kivirahealth.info | 2 |
| kivirahealth.live | 2 |
| kivirahealth.online | 3 |
| kivirahealth.xyz | 3 |
| scuttlewutt.com | 0 |

## Appendix B — Snapshot fields from `/v1/api/warmup/list` (prior REST script)

Warmup subscriptions cache reported `warmup_day` **8**, `warmup_status` **`in_progress`**, `health_score` **~98.4** for polled mailboxes (same calendar window as screenshots). Refresh before investor-facing summaries.

---

**Linked procedures:** wire `https://mcp.inboxkit.com/mcp` in Cursor for OAuth-backed MCP checks; repeat REST snapshots with `scripts/inboxkit_api_smoke.sh`; strategy context: [[TECH_STACK_OUTBOUND_INFRASTRUCTURE]], [[OUTREACH_BASELINE_METRICS]].
