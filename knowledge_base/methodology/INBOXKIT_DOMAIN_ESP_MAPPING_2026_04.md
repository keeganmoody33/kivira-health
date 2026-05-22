---
name: INBOXKIT_DOMAIN_ESP_MAPPING_2026_04
description: Six Namecheap sending domains imported to InboxKit with 4 Google + 2 Microsoft ESP split — domain list, rationale, and import CSV artifact.
domain: methodology
node_type: framework
status: emergent
last_updated: 2026-05-22
tags:
  - methodology
  - gtm-motion
  - outbound-infrastructure
  - gtm-tooling
topics:
  - outbound-infrastructure
  - gtm-motion
  - workflow
related_concepts:
  - "[[INBOXKIT_SENDKIT_SEQUENCER_ROADMAP]]"
  - "[[TECH_STACK_OUTBOUND_INFRASTRUCTURE]]"
  - "[[OUTREACH_WAVE_STRUCTURE]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[OUTBOUND_INBOX_SEND_VOLUME_MATH]]"
source:
  type: document
  file: "raw-context/kivira-internal/inboxkit-domain-import-2026-04-17.csv"
  date: "2026-04-13"
---

# InboxKit domain ESP mapping (April 2026)

Operational record for **six sending domains** registered via Namecheap (Order #199691847, 2026-04-13) and imported to InboxKit via CSV (`domain,esp` columns).

[VERIFIED: Domain list from Namecheap receipt; ESP assignment from operator decision in planning session 2026-05-22.]

## Domain inventory

| Domain | ESP | Role |
|--------|-----|------|
| kivirahealth.info | microsoft | Enterprise / Tier 3A–3C (M365-skew targets) |
| kivirahealth.live | microsoft | Enterprise / Tier 3A–3C |
| kivirahealth.xyz | google | Wave 1–3 bulk (1A, 1C, 2A, 2C) |
| kivirahealth.online | google | Wave 1–3 bulk (1B, 1C) |
| kivira.xyz | google | Shorter-brand variant; A/B within Google |
| kivira.online | google | Shorter-brand variant; A/B within Google |

## ESP split rationale (4 Google / 2 Microsoft)

- **Microsoft pair** — health systems, IDNs, regional payers (3A/3B/3C) skew Exchange/M365; mature TLDs (`info`, `live`) with explicit `kivirahealth` brand string.
- **Google quartet** — independent practices, mid-market groups, VBC, ACOs (1A–1C, 2A, 2C) skew Gmail/Google Workspace.
- **`kivirahealth.*` on both ESPs** — brand not confounded with ESP when comparing deliverability.
- **`kivira.*` Google-only** — clean A/B of brand recall within one ESP.

## Import artifact

Canonical CSV: [raw-context/kivira-internal/inboxkit-domain-import-2026-04-17.csv](../../raw-context/kivira-internal/inboxkit-domain-import-2026-04-17.csv)

```csv
domain,esp
kivirahealth.info,microsoft
kivirahealth.live,microsoft
kivirahealth.xyz,google
kivirahealth.online,google
kivira.xyz,google
kivira.online,google
```

Valid InboxKit `esp` values: `google`, `microsoft`, `both`.

## Post-import checklist

1. Verify all 6 domains show correct ESP in InboxKit before mailbox provisioning.
2. Configure DNS (SPF, DKIM, DMARC) in Namecheap Advanced DNS or delegate nameservers to InboxKit — **most common deliverability failure point**.
3. Confirm WHOIS privacy enabled on all six (Free Domain Privacy on Namecheap receipt).
4. Target **3 inboxes per domain → 18 mailboxes** ([[OUTBOUND_INBOX_SEND_VOLUME_MATH]]).
5. Warm **2–4 weeks** before production cold sends.

## Operational status note

As of [[WEEKLY_INBOXKIT_HEALTH_2026_05_04]], sixteen mailboxes were active across these six domains (warmup day ~8). Mailbox counts per domain may differ from 3×6 target during ramp — reconcile in weekly InboxKit evidence nodes.

## Related concepts

- [[INBOXKIT_SENDKIT_SEQUENCER_ROADMAP]] — next step after domains/mailboxes green
- [[TECH_STACK_OUTBOUND_INFRASTRUCTURE]] — stack ownership (Josh + Keegan)
- [[OUTREACH_WAVE_STRUCTURE]] — domain strategy for enterprise vs high-velocity cold
