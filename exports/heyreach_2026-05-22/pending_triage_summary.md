# HeyReach pending-lead triage — 2026-05-22

**Question asked:** of the leads still queued to send, who falls inside our 9 sub-tiers
**and** is a real decision-maker who could book a demo and ultimately purchase — and who
falls out of line?

**Triaged:** 949 leads = the full backing lists for the two campaigns holding all 717
pending sends (`Wave1-OperationalOwner` ← list 646679 "2A ACO Named Contacts", 359;
`Wave1-ClinicalChampion` ← list 646680 "1C Provider Group Personas", 590). We validate the
whole loaded set because HeyReach's API exposes no per-lead "pending" flag — re-judging the
already-sent minority is harmless.

> Note: the campaign display names are misleading. "OperationalOwner" actually holds **2A ACO
> named contacts**; "ClinicalChampion" holds **1C provider-group personas**. Triage uses the
> true list contents.

## Verdicts

| Verdict | Count | Meaning |
|---------|------:|---------|
| **KEEP** | **445** | In-tier decision-maker — Buyer or Champion, authority HIGH/MED. Can book a demo and/or buy. |
| **REVIEW** | **488** | In-tier but lower-authority, or no usable title to judge. Worth a 30-sec human look before sending. |
| **CUT** | **16** | Out of line — not our buyer, not in our sub-tiers. |

**KEEP roles:** 271 Buyers (purchase authority) + 174 Champions (book demos, drive internally).

### Per campaign (vs the 17% in-scope floor from the Wave-1 accept triage)
- **OperationalOwner / 2A ACO** (359): KEEP 192 (**53%**), REVIEW 161, CUT 6
- **ClinicalChampion / 1C ProvGroup** (590): KEEP 251 (**42%**), REVIEW 327, CUT 12

Both far exceed the 17% Wave-1 accept floor — expected, because these are curated *outbound*
lists (CMS ACO contacts + provider-group personas), not the inbound *accept* pool where vendor
spam dominated. **The noise problem was in who replied, not who we targeted.**

### KEEP by sub-tier × role
| | Buyer | Champion |
|---|---:|---:|
| **2A (ACO)** | 153 | 39 |
| **1C (Provider group)** | 118 | 133 |

## Why REVIEW is large (488)
- **202 — no title or headline at all.** HeyReach never enriched these (no title, no headline,
  no photo); a free join against `wave1_linkedin_master.csv` recovered 81, but the rest can only
  be resolved by an authenticated LinkedIn look (see Constraints). Not judgeable from data alone.
- **196 — low-authority operational roles** (Practice Administrator / Practice Manager / generic
  Director). Real, in-tier, demo-bookable, but lower purchase authority than a VP/C-suite — your call.
- **83 — title present but unmatched** (company-name-as-title noise, ambiguous strings).
- **7 — tech gatekeepers** (CMIO/CIO) — needed later, not the demo-booker.

## The 16 CUTs (all genuinely out of line)
Cybersecurity analyst, IT service-desk, a university student, 2 professors + a clinical professor,
QMS Manager at an aerospace firm (Aero Alliance), a "Head Coach", 3 retired, a recruiter,
3 medical assistants, a phlebotomy technician. None are healthcare decision-makers.
(Dual-title clinicians like "Medical Director … Associate Professor" are correctly **kept** — the
out-of-scope rule only fires when no decision-maker title is present.)

## Sample of strong keepers (Buyers, named org, has photo)
| Sub-tier | Title | Org |
|---|---|---|
| 2A | Executive Director | Alaska Primary Care Association |
| 2A | CEO | United Medical LLC |
| 2A | President & CEO | North Valley Nephrology |
| 2A | Chief Operating Officer | Jefferson Health Plans |
| 2A | Executive Director & Chief Operating Officer | Corewell Health |
| 2A | Sr. VP & Chief Financial Officer | St. Luke's University Health Network |
| 2A | Chief Executive Officer | VBCare Network LLC |
| 2A | Managing Partner/Founder | Costello Ginex & Wideikis, PC |

## Secondary signals
- **Profile photo** (HeyReach `imageUrl`): **374 / 445 KEEPs have one** (84%); 69 don't. Light
  quality flag, not a gate — a CMO without a HeyReach-cached photo is still a keeper.
- **"Is this person active":** not in the data. HeyReach's `connections`/`followers` are all 0
  (never populated) and LinkedIn blocks activity signals to unauthenticated tools.

## Known soft edge on the KEEP list
Triage judges the **title**, not the company. A handful of KEEPs are title-right but
company-questionable — e.g. "Owner @ Orion Communications, Inc." (a software firm, not a 2A ACO)
classifies as Buyer. Before sending, eyeball the `company` column on the KEEP list; the title
filter is strong, the company filter is light (these came from CMS/provider lists, so most
companies are legitimate, but a few slipped).

## Constraints that shaped this (so the numbers are read honestly)
1. **HeyReach API can't list campaign leads** — only aggregate counts. We pulled the leads via the
   list endpoint (`/list/GetLeadsFromList`), which the repo wasn't using; new puller:
   `scripts/heyreach_list_pull.py`.
2. **Spider profile-scrape doesn't work on LinkedIn unauthenticated** — it returns the
   "Sign Up | LinkedIn" wall, not the profile. So titles were recovered from our own master CSV
   (free), not scraped. The 202 no-title REVIEWs would need an authenticated browser pass to resolve.

## Artifacts
- `fixtures/heyreach_pending_2026-05-22/pending_triaged.csv` — full per-lead triage (the actionable file).
- `fixtures/heyreach_pending_2026-05-22/pending_raw.csv` / `pending_raw_enriched.csv` — source pull + title-recovery merge.
- `scripts/heyreach_list_pull.py`, `scripts/triage_pending_leads.py` — the pull + triage logic.

## Out of scope (Keegan's call)
Nothing was changed in HeyReach. Removing/pausing the CUT + REVIEW leads, and resolving the 202
no-title leads via an authenticated look, are follow-ups.
