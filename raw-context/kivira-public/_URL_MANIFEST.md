# Kivira public URL manifest (Firecrawl map + scrape)

**Generated:** 2026-04-03

## Discovered (firecrawl_map)

| URL | Notes |
|-----|--------|
| https://www.kivira.health | Marketing home |
| https://www.kivira.health/contact | Demo / inquiry form |
| https://www.kivira.health/team | Leadership + medical board |
| https://www.kivira.health/press | Placeholder (“Content inbound…”) at scrape time |
| https://www.kivira.health/contact-success | Thank-you / success page |
| https://www.kivira.health/legal/patient-app-terms-and-conditions | Patient app ToS |
| https://www.kivira.health/legal/privacy-policy | Privacy policy |
| https://www.kivira.health/sitemap.xml | Machine-readable index |
| https://instrument-overview.kivira.health | Clinical instruments + references (subdomain) |

## Exported markdown

- **Firecrawl:** `map` + `scrape` on www + `instrument-overview` subdomain (2026-04-03). Exports: `contact.md`, `team.md`, `press.md` (raw markdown from Firecrawl).
- **Jina reader (`r.jina.ai`):** Full-text archives for long legal + instrument + home pages: `jina-*.md` and canonical `www-home.md`, `legal-*.md`, `instrument-overview.md` (YAML frontmatter added).
- **`contact-success`:** Omitted (low GTM value); add if needed.

## Re-scrape cadence

After site launches or legal updates, re-map `https://www.kivira.health` and diff against this manifest.
