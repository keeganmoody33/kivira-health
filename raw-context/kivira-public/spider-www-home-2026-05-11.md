---
source_url: https://www.kivira.health/
scraped_at: 2026-05-11
extractor: spider-cloud
endpoint: "POST https://api.spider.cloud/crawl"
fidelity: medium
notable_delta: "Backer copy changed since 2026-04-06 scrape: 'Y Combinator & Antler' → 'Antler & major healthcare systems'"
note: "Spider HTTP-only crawl (no JS render). Pair with Jina reader for content embedded in Framer dynamic sections."
---

# Kivira marketing home — 2026-05-11 fresh scrape

Reproducible via:
```bash
python3 /tmp/spider_kivira_pull.py
```
(or roll into `scripts/` if this becomes a recurring pull)

## Diff vs `www-home.md` (2026-04-06)

| Field | April | May 11 | Notes |
|---|---|---|---|
| Tagline | "Solving mental health in primary care" | (same) | unchanged |
| Wedge framing | "PCPs are now the front line of mental health and they can't keep up" | (same) | unchanged |
| Value pillars | Accuracy / INTEGRATE / Quality | (same) | unchanged |
| Performance claims | PHQ-9 74%, GAD-7 82%, Y-BOCS 69%, TTFNET 65%, MINI 27% | (same) | unchanged |
| Clinical Advisory Report sample | Jenny Bloggs / PHQ-9 21 Severe / GAD-7 14 Moderate / C-SSRS 21 High Risk | (same) | unchanged |
| **Backer copy** | **"Backed by Y Combinator & Antler"** | **"Backed by Antler & major healthcare systems"** | **CHANGED — see KIVIRA_BACKER_COPY_SHIFT_2026_05 in knowledge_base** |

## Full content excerpt

```
Kivira | Solving mental health in primary care

Backed by top psychiatric research

Why Kivira
Kivira gives them the clarity, confidence, and tools to diagnose and treat with precision.

Accuracy
We combine evidence-based screening, digital phenotyping, and AI analytics aligned with DSM-5 criteria
to deliver accurate, reproducible mental-health diagnoses — improving treatment decisions and patient outcomes.

INTEGRATE
We fit directly into your existing EHR workflow. Screen and prescribe without extra steps —
everything works naturally within how you already practice.

Quality
We combine evidence-based screening, digital phenotyping, and AI analytics aligned with DSM-5 criteria
to deliver accurate, reproducible mental-health diagnoses — improving treatment decisions and patient outcomes.

##### Time-discounted accuracy
Faster and more accurate than existing tools, scores indicate better time-adjusted performance.
27% MINI
27% TTFNET
65% Y-BOCS
69% (Y-BOCS column — appears to be a row label artifact)
74% PHQ-9
82% GAD-7

Backed by Antler & major healthcare systems
```

[VERIFIED: Captured 2026-05-11 ~21:08 EDT via Spider Cloud `/crawl` endpoint with `request: http`, `lite_mode: true`. Full markdown also at `/tmp/kivira-home-fresh.md`.]
