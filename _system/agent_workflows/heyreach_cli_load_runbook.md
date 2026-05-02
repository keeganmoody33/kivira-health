# HeyReach CLI Load Runbook — Wave 1 (2A + 1C)

**Last updated:** 2026-05-01  
**Status:** Ready to execute  
**CLI tool:** https://github.com/bcharleson/heyreach-cli (npm, unofficial but trusted)  
**Auth:** `HEYREACH_API_KEY` env var

---

## Pre-flight

```bash
# Verify CLI is installed and authenticated
heyreach --version
heyreach lists list          # should return your existing lists (may be empty)

# Confirm lead files are ready
wc -l fixtures/heyreach_loads/heyreach_leads_2a.json   # should be >1 line (JSON array)
wc -l fixtures/heyreach_loads/heyreach_leads_1c.json
python3 -c "
import json
a = json.load(open('fixtures/heyreach_loads/heyreach_leads_2a.json'))
b = json.load(open('fixtures/heyreach_loads/heyreach_leads_1c.json'))
print(f'2A: {len(a)} leads, 1C: {len(b)} leads')
"
# Expected: 2A: 340 leads, 1C: 582 leads
```

**Current lead counts (as of 2026-05-01 build):**
- 2A (ACO named contacts): **340 leads** — well under 1000 limit, single `add-leads` call
- 1C (provider group personas): **582 leads** — well under 1000 limit, single `add-leads` call

---

## Step 1 — Create lists

Create two lists: one per tier. Use the IDs returned in subsequent steps.

```bash
# Create the 2A list
heyreach lists create --name "Wave 1 — 2A ACO Named Contacts (2026-05-01)"

# Create the 1C list
heyreach lists create --name "Wave 1 — 1C Provider Group Personas (2026-05-01)"

# Capture the list IDs
heyreach lists list
# Output will show list IDs — copy them for steps below
```

---

## Step 2 — Load 2A leads

```bash
# From repo root — 340 leads, fits in one call
heyreach lists add-leads \
  --list-id LIST_ID_2A \
  --leads-json "$(cat fixtures/heyreach_loads/heyreach_leads_2a.json)"
```

**What each lead contains:**
- `profileUrl` — LinkedIn URL (precision-filtered by contact name + ACO org tokens)
- `firstName` / `lastName` — split from CMS-provided exec contact name
- `companyName` — ACO name from CMS MSSP PY2026 CSV
- `position` — blank (HeyReach enriches from profile)

---

## Step 3 — Load 1C leads

```bash
# From repo root — 582 leads, fits in one call
heyreach lists add-leads \
  --list-id LIST_ID_1C \
  --leads-json "$(cat fixtures/heyreach_loads/heyreach_leads_1c.json)"
```

**What each lead contains:**
- `profileUrl` — LinkedIn URL (filtered: persona title token must appear in SERP result)
- `firstName` / `lastName` — empty (no named contact in CMS data for 1C)
- `companyName` — provider group org name from CMS MSSP PY2026 CSV
- `position` — blank

---

## Step 4 — Verify

```bash
# Check list contents
heyreach lists list

# Or check counts via API (if CLI supports it):
heyreach lists get --list-id LIST_ID_2A
heyreach lists get --list-id LIST_ID_1C
```

Expected: 340 leads in 2A list, 582 in 1C list.

---

## Regenerating the files

If you need to rebuild the lead files (e.g., after a new Spider run or to adjust precision filter):

```bash
# Rebuild both from existing JSONL (no new Spider calls):
python3 scripts/build_heyreach_load.py --mode both

# Tighter precision (only very high-confidence hits):
python3 scripts/build_heyreach_load.py --mode both \
  --min-id-matches 2 \
  --min-org-matches 2

# Point to a different run's JSONL:
python3 scripts/build_heyreach_load.py --mode 2a \
  --jsonl fixtures/wave1_runs/<RUN_DIR>/Q2A_progress.jsonl
```

---

## Batching (if counts exceed 1000)

HeyReach CLI accepts up to 1000 leads per `add-leads` call. Current counts are well under.
If a future run produces >1000, use this splitter:

```bash
python3 - <<'EOF'
import json
for label, path in [("2a", "fixtures/heyreach_loads/heyreach_leads_2a.json"),
                    ("1c", "fixtures/heyreach_loads/heyreach_leads_1c.json")]:
    leads = json.load(open(path))
    for i, batch in enumerate([leads[j:j+1000] for j in range(0, len(leads), 1000)]):
        out = f"fixtures/heyreach_loads/heyreach_leads_{label}_batch{i}.json"
        open(out, "w").write(json.dumps(batch))
        print(f"Wrote {len(batch)} leads → {out}")
EOF
```

---

## Sequence → Campaign wiring

After loading lists into HeyReach, wire them to a campaign/sequence in the HeyReach UI:

1. Go to **Campaigns** → select or create the Wave 1 campaign
2. Under **Leads** → select the list you just loaded
3. Confirm the connection-request note template is active (persona-specific copy from the outbound campaign plan)
4. Set daily send cap: **25 connections/day** (1 sender, LinkedIn Premium)
5. Launch: **May 4, 2026** (Wave 1A start date per campaign plan)

---

## Related scripts

| Script | Purpose |
|--------|---------|
| `scripts/spider_account_search.py` | Runs Spider SERP searches, writes JSONL |
| `scripts/build_heyreach_load.py` | JSONL → HeyReach JSON (this pipeline stage) |
| `scripts/export_heyreach_leads.py` | Legacy exporter (different schema — do not use for JSONL input) |
| `scripts/build_list_1c_2a.py` | CMS MSSP CSV → wave1_raw_accounts.csv |

---

## Open items

- [ ] LinkedIn Premium upgrade — required before May 4 launch (LEC-39, resolved in decision; action pending on user)
- [ ] NPPES Type-2 bulk CSV download — needed for Wave 1A / 1B provider group list (re-download from https://download.cms.gov/nppes/NPI_Files.html)
- [ ] 1C connection-note copy — not drafted yet; out of scope until post-accept flow discussion
