# Wave 1 — Small-batch iteration (demos & feedback)

**Purpose:** Ship **20–30 connection requests per subtier code** per round, prioritizing leads most likely to **accept quickly** so you learn what works before scaling volume.

**Reality check:** The Parallel extractor does **not** see LinkedIn activity (posts, frequency, last active). **Accept-speed proxies** in-repo are: `signal_score`, keyword-matched titles (`persona_confidence` high), `subtier_confidence`, and BH persona bump — see `scripts/export_heyreach_leads.py` (`accept_priority`). For real “active on LinkedIn” filtering later, enrich via Clay/Apollo or Sales Nav list export and merge.

---

## Batch sizing

| Knob | Suggestion |
|------|------------|
| Per subtier per round | **20–30** (`--per-subtier 30`) |
| Tier focus | Tier 1–2 first (`--only-tier-1-2`); Tier 3 optional, smaller batches |
| Min signal | Start **25**; raise to **30** if volume is noisy |

Generate upload files:

```bash
python3 scripts/export_heyreach_leads.py --per-subtier 30 --min-signal 25 -o fixtures/wave1_heyreach_ready.csv
```

Optional Tier 1–2 only:

```bash
python3 scripts/export_heyreach_leads.py --per-subtier 25 --only-tier-1-2
```

**Columns `accept_priority` and `subtier_code`** are for sorting/review; remove them in Sheets before HeyReach import if your importer rejects extra fields.

---

## 6-day accept window (operational)

1. **Day 0:** Load batch → connection requests go out (respect HeyReach daily caps).
2. **Day 6:** Anyone **not accepted** → **pause or remove** from the active sequence for that campaign (do not let stale invites clutter the experiment). Replace with the **next** names from `wave1_linkedin_master.csv` (re-export with `--per-subtier` after excluding URLs already processed — use `heyreach_campaign` / notes).
3. **Track** accepts in `output/wave1a_demo_funnel.csv` (or a shared sheet): **time-to-accept** if you log the send date.

Fast iteration = **high accept_priority first**, short cycles, swap cold URLs weekly.

---

## Cadence

- Prefer **one persona campaign live first** (Operational Owner per `COCM_OUTREACH_SEQUENCING`), small batch, read reply/accept rates after ~50 invites across subtier mix.
- Scale daily caps only after accept rate stabilizes or copy changes.

---

**Created:** 2026-05-02  
**Related:** [[heyreach-mcp-load-runbook]] · [[COCM_OUTREACH_SEQUENCING]]
