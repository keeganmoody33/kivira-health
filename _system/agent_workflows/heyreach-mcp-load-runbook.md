# HeyReach MCP Load Runbook

**Purpose:** Step-by-step instructions for loading enriched LinkedIn URLs from `fixtures/wave1_linkedin_master.csv` into HeyReach campaigns via the MCP server in Cursor. No Python loader needed — the MCP makes this an interactive operation.

**Demo / feedback phase (pre-revenue):** Sourcing will naturally mix **Tier 1 and Tier 2** subtiers (1A–2C); Tier 3 (3A/3B/3C) may appear—do not treat Tier 3 as the primary target for outbound, but **do not exclude** Tier 3 rows from the export if they land in the master and pass quality gates (enterprise rhythm differs when you engage).

**HeyReach-ready file:** Run `python3 scripts/export_heyreach_leads.py` to write `fixtures/wave1_heyreach_ready.csv` with columns mapped for paste/import (`profileUrl`, `firstName`, `lastName`, etc.). Optional: `--only-tier-1-2` if you want to batch only 1A–2C for a given send.

**Small batches (20–30 per subtier, fast iteration):** See [`wave1-small-batch-iteration.md`](wave1-small-batch-iteration.md). Example: `python3 scripts/export_heyreach_leads.py --per-subtier 25`

**Prerequisites:**
- `.cursor/mcp.json` configured with `heyreach` server (DONE)
- `HEYREACH_API_KEY` available in env or hardcoded in mcp.json
- Cursor restarted to pick up MCP config
- Wave 1 pipeline has run and `fixtures/wave1_linkedin_master.csv` has rows

---

## One-Time Setup (HeyReach UI — do this first)

In HeyReach, create 5 campaigns. **They must be ACTIVE with LinkedIn senders attached** before lead-add will work.

| Campaign Name | Persona | Primary Theme |
|---------------|---------|---------------|
| `Wave1-OperationalOwner` | operational_owner | Workflow / Ops |
| `Wave1-ClinicalChampion` | clinical_champion | Clinical Outcomes |
| `Wave1-EconomicBuyer` | economic_buyer | ROI / Revenue |
| `Wave1-TechGatekeeper` | tech_gatekeeper | Technical / Integration |
| `Wave1-BHQualityInfluencer` | bh_quality_influencer | Quality / Compliance |

**Daily caps:** 25 connection requests/day per campaign on HeyReach Growth.

After creating, capture the campaign IDs into `fixtures/wave1_campaign_ids.json`:

```json
{
  "operational_owner": "<id>",
  "clinical_champion": "<id>",
  "economic_buyer": "<id>",
  "tech_gatekeeper": "<id>",
  "bh_quality_influencer": "<id>"
}
```

---

## Per-Run Load Procedure

After every Spider → Parallel pipeline run, do the following from a Cursor chat session:

### Step 1 — Confirm campaigns are reachable

> Use the heyreach MCP `get-active-campaigns` tool and confirm all 5 Wave1 campaigns appear with status ACTIVE.

If any campaign isn't active, fix in HeyReach UI before proceeding.

### Step 2 — Filter master.csv by persona

> Run `python3 scripts/export_heyreach_leads.py` first — inspect row counts in stdout — or read `fixtures/wave1_linkedin_master.csv` manually.
>
> Include rows where `persona` ≠ `unknown`, `persona_confidence` ∈ {high, medium}, and `signal_score` ≥ 25 (default export threshold; use `--min-signal 30` to tighten).
>
> **Subtier:** Tier 1–2 (1A–2C) is the practical focus for demos and feedback; Tier 3 rows can load when they appear—expect longer cycles. To export **only** 1A–2C for a batch: `python3 scripts/export_heyreach_leads.py --only-tier-1-2`.
>
> Emit a per-persona summary:
>
> - operational_owner: N rows
> - clinical_champion: N rows
> - … etc.
>
> Show me the totals before loading anything.

### Step 3 — Load one persona at a time

For each persona above, in order Operational Owner → Clinical Champion → Tech Gatekeeper → Economic Buyer → BH/Quality Influencer (per `COCM_OUTREACH_SEQUENCING`):

> Use heyreach MCP `add-leads-to-campaign` with `campaignId = <Wave1-OperationalOwner ID>` and the operational_owner rows from master.csv. Map fields:
>
> - profileUrl ← linkedin_profile_url
> - firstName, lastName ← split full_name
> - companyName ← current_company
> - position ← current_title
>
> Add custom variables:
> - subtier ← subtier_guess
> - signal ← signal_score
>
> Batch up to 1000 leads per call. Report addedCount when done.

### Step 4 — Update heyreach_campaign column

After each persona's batch lands cleanly:

> Update `fixtures/wave1_linkedin_master.csv` — set `heyreach_campaign` column to `Wave1-OperationalOwner` for every row that was just loaded. This is our audit trail so we don't double-load on the next run.

### Step 5 — Sequencing gates

**Per `COCM_OUTREACH_SEQUENCING`:**

- ✅ Operational Owner — launch immediately after load
- ⏸ Clinical Champion — load now, **leave campaign paused**. Resume only when Operational Owner accept-rate ≥ 25%.
- ⏸ Tech Gatekeeper — load and pause. Resume in parallel with Operational Owner once first reply lands.
- 🚫 Economic Buyer — **load but do not launch** until at least one warm thread exists at the same account.
- 🚫 BH/Quality Influencer — load only when a demo is on the calendar.

---

## Re-Run Hygiene

Every subsequent Spider → Parallel run only adds NEW URLs to master.csv (deduped). To load only the new rows:

> Read fixtures/wave1_linkedin_master.csv (or `fixtures/wave1_heyreach_ready.csv` after export) and filter rows where heyreach_campaign is empty AND persona_confidence ∈ {high, medium} AND signal_score ≥ 25 (or your chosen minimum). Group by persona and proceed with steps 3-4 above.

---

## Failure Modes & Recovery

| Symptom | Cause | Fix |
|---------|-------|-----|
| `add-leads-to-campaign` returns 401 | API key wrong/missing | Verify `.cursor/mcp.json` env block |
| `addedCount` < submitted count | Some URLs already in campaign | Normal; HeyReach dedupes per-campaign automatically |
| Campaign appears inactive | Senders disconnected or paused | Reconnect LinkedIn account in HeyReach UI |
| LinkedIn account flagged | Daily cap exceeded over time | Drop daily cap to 20; pause 24h |
| MCP tool not found in Cursor | Cursor didn't pick up `.cursor/mcp.json` | Cursor → Settings → MCP → reload, or restart Cursor |

---

## Why MCP-driven, not scripted

We deliberately avoided writing a Python `heyreach_loader.py` because:
1. **Visibility.** MCP tool calls show up in Cursor's tool log. A Python script's failure is silent until you read the logs.
2. **Stop-the-line moments.** If a batch looks wrong, you abort by closing the Cursor chat. A script keeps going.
3. **Lower friction.** No auth code, no SDK install, no virtualenv. The MCP is already wired.
4. **Composability.** The same MCP supports `pause-campaign`, `get-leads`, `get-stats` — the runbook can grow without new scripts.

If volume eventually warrants automation (say, daily 1,000+ adds), the MCP server itself can be invoked in JSON-RPC mode from a script. We'll cross that bridge if we ever cross it.

---

**Created:** 2026-05-01
**Status:** Active
**Related:** [[heyreach-zero-budget-sourcing]] · [[COCM_OUTREACH_SEQUENCING]] · [[BUYING_COMMITTEE_DYNAMICS]]
