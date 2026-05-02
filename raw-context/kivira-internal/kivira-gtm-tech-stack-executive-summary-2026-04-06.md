# Kivira GTM Tech Stack Executive Summary

**Date:** 2026-04-06
**Prepared for:** Keegan Moody, Josh Pappas · **Audience:** Kivira leadership (budget & strategy alignment)
**Classification:** Internal — Operational Planning
**Related:** [[GTM_30_60_90_EXECUTION_CADENCE]] · [[OUTREACH_WAVE_STRUCTURE]] · [[THIRTY_DAY_OFFICE_MANAGER_TARGET]] · [[TECH_STACK_OUTBOUND_INFRASTRUCTURE]]

---

## Ops ownership (read this first)

**Josh Pappas and Keegan Moody** own GTM outbound for this stack: vendor selection, procurement, renewals, account administration, integrations, and secure credential handling (shared vault or ops-owned identities). **The founder is not expected to buy tools, receive API keys or passwords for routine execution, or operate as the day-to-day admin** for these systems. If the company places subscriptions on a corporate card under a specific name for finance reasons, GTM ops still retain admin access and secrets—this is not a “purchase and Slack me the codes” workflow.

**What we need from leadership:** Alignment on monthly spend bands, runway tolerance, and go/no-go on strategic upgrades (e.g., Clay, sequencer scale tiers). This document informs those decisions; execution stays with Josh and Keegan.

---

## 1. Executive Summary

Kivira needs a go-to-market stack that can find the right primary care accounts, identify the right people inside buying committees, reach them across email and LinkedIn simultaneously, and track every interaction through to pilot conversion — all while operating within healthcare compliance norms and a pre-seed budget.

This document recommends a 10-layer stack built around **Claude Code as the orchestration brain**, with dedicated tools for email sequencing, LinkedIn automation, inbox provisioning, contact enrichment, CRM, and phone outreach. The architecture is designed to support account-based, multichannel outbound into a healthcare B2B market where buyers are evidence-sensitive, procurement cycles involve 3-4 persona types, and proof-of-value windows are short.

**What to buy now:** Email infrastructure, sequencer, enrichment, LinkedIn tools, and a dialer. These are required to hit the Day 30 milestone of 5 live office manager conversations.

**What to defer:** Dedicated CRM (Smartlead's built-in or Airtable Free covers Phase 1), workflow automation between systems, and advanced analytics tooling. These become relevant at Day 30-60 when data flows between systems at volume.

**Estimated monthly spend:**

| Tier | Monthly | Annual |
|------|---------|--------|
| Lean MVP | ~$460–500 | ~$5,500–6,000 |
| Recommended Core | ~$700–760 | ~$8,400–9,100 |
| Scale-Ready | ~$880–950 | ~$10,600–11,400 |

**Highest-risk unknowns:**
1. Whether email deliverability to healthcare admin inboxes holds at projected rates — healthcare domains are aggressive spam filters
2. Whether the 40+ field account schema can live in a free-tier CRM without friction, or forces a $14+/mo Pipedrive commitment early
3. Whether Clay's waterfall enrichment materially improves on LeadMagic/Wiza standalone — the $167-185/mo delta needs to earn its keep
4. Whether the market responds to operator-first outreach (office managers) or demands clinical-champion-first messaging — this determines sequencing logic across the entire stack

---

## 2. Kivira GTM Operating Context

This stack must support a specific GTM model — not generic SaaS outbound.

### The motion

Kivira sells clinical decision support for behavioral health into primary care. The wedge is PCPs who are already the frontline for mental health care but lack structured screening and decision-support tooling. The buyer environment is evidence-sensitive, operationally constrained, and procurement-heavy.

### What the stack must do

| Operating Need | Why It Matters | Stack Implication |
|----------------|----------------|-------------------|
| **Account identification** | ~23,700 target accounts across 9 subtiers, sourced from NPPES, CMS, HRSA public data | Need a research/orchestration layer (Claude Code) that builds lists from public registries, not just purchased databases |
| **Contact enrichment** | Must find office managers, practice admins, clinical directors — not just C-suite | Need enrichment tools that resolve person-level contacts from org-level data (LeadMagic/Wiza + Clay waterfall) |
| **Persona mapping** | 3-persona buying committee (clinical champion, technology gatekeeper, operational buyer) with strict sequencing: operator first, clinical second, economic third | CRM must track persona type per contact and support multi-threaded account views |
| **Subtier segmentation** | 9 subtiers across 3 tiers with different outreach rules, evidence grades, and messaging | Sequencer must support segment-based campaign logic; enrichment must tag subtier membership |
| **Multichannel outbound** | Email + LinkedIn running in parallel against the same prospect list | Need both an email sequencer and LinkedIn automation tool with shared lead data |
| **Evidence-governed claims** | CoCM revenue estimates can only be used in outbound above confidence Grade B | Messaging discipline must be enforced at the campaign level, not just in templates |
| **Pilot-first sales motion** | Every CTA frames toward low-friction pilot setup with short time-to-value | Pipeline tracking needs pilot stage management, not just deal stages |
| **Healthcare compliance awareness** | Buyers expect HIPAA-ready vendors; any tool touching prospect data must not inadvertently handle PHI | Stack should avoid tools that require storing patient data; outreach data is prospect/business data, not clinical |
| **30-day proof of output** | Day 30 milestone: 5 office managers on the phone | Stack must be operational within 2-3 weeks, not 2-3 months |

### The constraint

Kivira is pre-seed. The stack must be lean enough to run with 1-2 operators, elegant enough to scale when funding arrives, and opinionated enough that Claude Code can orchestrate workflows without manual glue logic at every step.

---

## 3. Recommended Stack Architecture

| Layer | Job To Be Done | Recommended Tool | Backup Option | Est. Monthly | Est. Annual | Pricing Model | Pricing Link | Why It Fits Kivira | Risks / Notes |
|-------|---------------|-----------------|---------------|-------------|------------|---------------|-------------|-------------------|---------------|
| **AI Workspace / Orchestration** | List building, research, account scoring, CoCM estimation, workflow orchestration | **Claude Code Max 20x** | Claude Code Pro ($20/mo) | $200 | $2,400 | Flat subscription | [claude.com/pricing](https://claude.com/pricing) | This is the operating system. Persistent memory, extended reasoning, and 20x capacity handle the volume of multi-step research and orchestration workflows Kivira runs | Anthropic usage limits may throttle during heavy orchestration sprints; Pro tier ($20) is viable fallback but capacity-constrained |
| **Email Sequencing** | Send multichannel email sequences with mailbox rotation, warmup, open/reply tracking | **Instantly Growth** | Smartlead Base ($39/mo) | $37–47 | $444–564 | Per-plan, unlimited accounts | [instantly.ai/pricing](https://instantly.ai/pricing) | Unlimited email accounts + built-in warmup on all plans. Larger ecosystem, more integrations, simpler UX. Sufficient for Phase 1 volume (1K active leads, 5K emails/mo) | 1,000 active lead cap on Growth plan. Scale to Hypergrowth ($97/mo) at Day 30-60 if volume demands. Smartlead has better rotation logic if deliverability is an issue |
| **Email Sequencing (Scale)** | A/B testing, advanced analytics, higher volume | **Instantly Hypergrowth** | Smartlead Pro ($94/mo) | $97 | $1,164 | Per-plan | [instantly.ai/pricing](https://instantly.ai/pricing) | 25K leads, 100K emails/mo. A/B testing unlocked. Scale tier for Day 30+ | Only needed after validating messaging in Growth tier |
| **Email Infrastructure** | Provision pre-warmed inboxes with automated DNS, SPF, DKIM, DMARC | **Zapmail Growth** | ScaledMail ($199/mo) | $99 | $1,188 | Per-plan + per-inbox add-ons | [zapmail.ai](https://zapmail.ai) | 30 Google Workspace mailboxes, pre-warmed, automated DNS. Modular — start small, scale up. Real Google Workspace accounts (better deliverability than custom infra) | ScaledMail ($199 flat) is simpler: 196 inboxes, 4 domains, no decisions. Trade-off: ScaledMail uses own infra, not Google Workspace. Zapmail Pro ($299) adds API for programmatic provisioning from Claude Code |
| **Domain Registration** | Register sending domains separate from kivira.health | **Porkbun** | Cloudflare Registrar (~$10.44/yr) | ~$5 | ~$55–88 | Per-domain annual | [porkbun.com/products/domains](https://porkbun.com/products/domains) | Transparent pricing ($11/yr .com), renewal = registration, free WHOIS privacy, bulk-friendly | Check whether Zapmail/ScaledMail includes domains. If so, this is supplemental only. Diversify registrars to avoid correlated blacklisting |
| **Contact Enrichment (Primary)** | Verify emails and phone numbers for target contacts | **LeadMagic Essential** | Wiza Email ($99/mo) | $100 | $1,200 | Credit-based, pay-per-result | [leadmagic.io/pricing](https://leadmagic.io/pricing) | 10K credits/mo, credits roll over, only charged for valid results. 19-endpoint API (email finder, validation, company enrichment, mobile numbers). No Sales Nav dependency. $0.008/credit | Wiza claims 99% vs. LeadMagic's 97% email accuracy. Wiza requires Sales Nav subscription. LeadMagic's rollover credits are better for uneven usage patterns |
| **Contact Enrichment (Waterfall)** | Fill gaps on contacts primary enrichment can't find | **Clay Launch** | Manual LinkedIn lookup ($0) | $167–185 | $2,004–2,220 | Credit-based (data credits + actions) | [clay.com/pricing](https://www.clay.com/pricing) | Waterfall enrichment across 75+ data providers — checks sequentially until a result is found. Integrates directly with HeyReach for dynamic personalization. 2,500 data credits, 15K actions | Largest recurring line item after Claude Code. Defer to Recommended Core tier — validate LeadMagic standalone first in Lean MVP. March 2026 pricing overhaul cut costs 50-90%; no charge for failed lookups |
| **LinkedIn Research** | Find and validate buyers, build lead lists, InMail | **Sales Navigator Core** | Free LinkedIn ($0) | $90–99 | $1,080–1,188 | Per-seat subscription | [business.linkedin.com/sales-solutions/compare-plans](https://business.linkedin.com/sales-solutions/compare-plans) | Advanced search filters, lead lists, InMail credits. Essential for buyer research in healthcare where org charts are opaque. Powers Wiza enrichment if chosen. 30-day free trial available | $99/mo is significant at pre-seed. Start with 30-day free trial during Week 1-2 warmup period. If LeadMagic is enrichment tool, Sales Nav value is research-only |
| **LinkedIn Automation** | Automate connection requests, profile visits, message sequences | **HeyReach Growth** | Manual LinkedIn outreach ($0) | $59–79 | $708–948 | Per-sender seat | [heyreach.io/pricing](https://www.heyreach.io/pricing) | Automated LinkedIn sequences running parallel to email. Dynamic personalization variables from Clay integration. 1 sender seat. 14-day free trial (3 seats, no CC) | LinkedIn automation carries platform risk — LinkedIn can restrict accounts if automation is detected. HeyReach's rotation and throttling mitigate this. Start conservative |
| **CRM / Pipeline** | Track accounts, contacts, deals, multi-threaded buying committees | **Airtable Free** | Pipedrive Essential ($14/user/mo) | $0 | $0 | Freemium | [airtable.com/pricing](https://airtable.com/pricing) | Unlimited custom fields (fits 40+ field account schema), 1,000 records free. Schema-flexible. Claude Code can read/write via API | No pipeline UX — it's a database, not a sales CRM. Pipedrive ($14/mo) adds real pipeline management with unlimited custom fields. HubSpot Free (10 custom property cap) cannot support the 40+ field schema without $90/mo upgrade |
| **Phone / Dialer** | Call office managers and practice admins | **Trellus Free** | Quo Starter ($15–19/mo) | $0 | $0 | Freemium + per-seat paid | [trellus.ai/pricing](https://www.trellus.ai/pricing) | Free plan: 30 power dials/week with AI summaries, transcripts, follow-ups. Chrome extension — embeds into existing workflows, no separate phone system. YC-backed | 30 dials/week is more than enough for 5-call Day 30 target. Power plan ($59.99/mo) adds unlimited single-line dialing + voicemail drop. Parallel plan ($149.99/mo) adds multi-line for scale. Quo ($15-19/mo) is the pick if you want a dedicated business phone number with texting |
| **Healthcare Account Data** | Org + clinician + affiliation data for primary care targets | **CarePrecise** | NPPES + CMS public data ($0) | — | — | One-time purchase | Not publicly listed — estimated $300–500 from prior research | Healthcare-specific dataset: org structures, clinician affiliations, specialty breakdowns. Closest substitute for Definitive Healthcare at a fraction of cost | One-time purchase, not SaaS. Data ages — plan to refresh annually. Free public sources (NPPES, CMS, HRSA, NCQA, PECOS) cover baseline; CarePrecise fills affiliation gaps |

---

## 4. Pricing Options

### Lean MVP Stack — ~$460–500/mo (~$5,500–6,000/yr)

Get sending on email + LinkedIn. Manual enrichment gaps. Claude Code does the heavy orchestration.

| Tool | Monthly |
|------|---------|
| Claude Code Max 20x | $200 |
| Instantly Growth (annual) | $37 |
| Zapmail Starter (10 inboxes) | $39 |
| Porkbun domains (5 .com) | ~$5 |
| LeadMagic Basic (2,500 credits) | $60 |
| Sales Navigator Core (annual) | $90 |
| HeyReach Growth (annual) | $59 |
| Trellus Free | $0 |
| Airtable Free | $0 |
| **Total** | **~$490** |

**One-time:** CarePrecise ~$300–500

**Capability gained:** Multichannel outbound (email + LinkedIn), AI-powered list building and research, basic contact enrichment, pre-warmed email infrastructure, parallel dialing with AI transcription, CRM-flexible account tracking.

**Capability sacrificed:** No waterfall enrichment (Clay) — enrichment gaps require manual LinkedIn lookup. Limited to 10 inboxes and 1,000 active leads. No dedicated CRM pipeline UX. No voicemail drop (Trellus Free limitation).

---

### Recommended Core Stack — ~$700–760/mo (~$8,400–9,100/yr)

Core automation on both channels. Clay fills enrichment gaps. Upgraded email infra.

| Tool | Monthly |
|------|---------|
| Claude Code Max 20x | $200 |
| Instantly Growth (annual) | $37 |
| Zapmail Growth (30 inboxes) | $99 |
| Porkbun domains (5-8 .com) | ~$5 |
| LeadMagic Essential (10K credits) | $100 |
| Clay Launch | $167–185 |
| Sales Navigator Core (annual) | $90 |
| HeyReach Growth (annual) | $59 |
| Trellus Free | $0 |
| Airtable Free | $0 |
| **Total** | **~$757–775** |

**One-time:** CarePrecise ~$300–500

**Capability gained:** Everything in Lean MVP plus waterfall enrichment across 75+ providers (Clay), 10K enrichment credits with rollover, 30 pre-warmed inboxes, Clay → HeyReach integration for dynamic LinkedIn personalization.

**Capability sacrificed:** No dedicated CRM pipeline (still Airtable or Smartlead built-in). No A/B testing on email sequences (Growth plan limitation). No parallel dialing (Trellus Free is single-line).

---

### Scale-Ready Stack — ~$880–950/mo (~$10,600–11,400/yr)

Everything running. Upgraded sequencer. Dedicated CRM. Parallel dialing.

| Tool | Monthly |
|------|---------|
| Claude Code Max 20x | $200 |
| Instantly Hypergrowth | $97 |
| ScaledMail (196 inboxes, 4 domains) | $199 |
| LeadMagic Essential (10K credits) | $100 |
| Clay Launch | $167–185 |
| Sales Navigator Core (annual) | $90 |
| HeyReach Growth (annual) | $59 |
| Trellus Power | $60 |
| Pipedrive Essential | $14 |
| **Total** | **~$986–1,004** |

**One-time:** CarePrecise ~$300–500

**Capability gained:** Everything in Core plus A/B testing and 25K active leads (Instantly Hypergrowth), 196 inboxes with zero provisioning decisions (ScaledMail), real pipeline CRM (Pipedrive), unlimited power dialing with voicemail drop (Trellus Power).

**Capability sacrificed:** Nothing material. This is the full operational stack. Monthly cost may be aggressive for pre-seed if runway is constrained.

---

## 5. Context OS Mapping

How each stack component maps into the Kivira Context OS operating model:

| Context OS Module | Purpose | System of Record | Inputs | Outputs | Human Owner | Automation Trigger | Downstream Dependency |
|-------------------|---------|-----------------|--------|---------|-------------|-------------------|----------------------|
| **Accounts** | Maintain canonical list of target organizations across 9 subtiers | Airtable / Pipedrive | NPPES, CMS, CarePrecise, Claude Code research | Scored account list with subtier tags, CoCM estimates | Josh + Keegan (GTM ops) | Claude Code builds/updates weekly from public data sources | Contacts, Segments, Outreach Sequences |
| **Contacts** | Person-level records with verified email, phone, LinkedIn, persona type | Airtable / Pipedrive + LeadMagic/Clay | Account list, LinkedIn, enrichment APIs | Verified contact records with persona tags (operator, clinical, technical, economic) | Josh + Keegan (GTM ops) | LeadMagic API call per new account; Clay waterfall for gaps | Outreach Sequences, Buying Committee |
| **Segments / Subtiers** | Tag accounts into 9 subtiers (1A–3C) with corresponding outreach rules | Airtable / Pipedrive | Account data, ACCOUNT_SCHEMA_EXTENDED fields, GTM_TIER_ARCHITECTURE | Subtier assignments driving campaign routing | Josh + Keegan (GTM ops) | Claude Code assigns subtier on account creation using scoring rules | Outreach Sequences, Messaging Library |
| **Buying Committee** | Map multi-persona threads per account (operator → clinical → economic → technical) | Airtable / Pipedrive | Contact records with persona type, BUYING_COMMITTEE_DYNAMICS rules | Per-account committee map showing thread status | Josh + Keegan (GTM ops) | Manual mapping informed by Claude Code research | Outreach Sequences, Pilot Pipeline |
| **Messaging Library** | Maintain hypothesis-stage messaging variants by subtier and persona | Context OS knowledge_base | MESSAGING_HYPOTHESIS_DISCIPLINE, COCM_OUTREACH_SEQUENCING, A/B test results | Tested message templates with performance data | Josh + Keegan (GTM ops) | Claude Code drafts variants; human approves before launch | Outreach Sequences |
| **Outreach Sequences** | Execute multichannel campaigns (email via Instantly/Smartlead + LinkedIn via HeyReach) | Instantly or Smartlead (email) + HeyReach (LinkedIn) | Contact records, messaging templates, subtier routing rules | Sent sequences with open/reply/acceptance tracking | Josh + Keegan (GTM ops) | Contacts loaded to sequencer trigger campaign start; Clay auto-pushes to HeyReach | Pilot Pipeline, Proof/ROI |
| **Research / Market Intel** | Capture competitive intelligence, market signals, account-specific research | Context OS knowledge_base + Claude Code memory | Web research, Firecrawl scrapes, call notes, public filings | Knowledge nodes with source attribution and evidence tags | Josh + Keegan (GTM ops) | Claude Code ingests artifacts weekly per CONTEXT_OS_OPERATING_RHYTHM | Messaging Library, Accounts |
| **Pilot Pipeline** | Track accounts from first reply through to active pilot | Airtable / Pipedrive | Reply data from sequencer, call notes from Trellus/Quo, manual status updates | Pipeline stages: Replied → Call Scheduled → Call Complete → Pilot Proposed → Pilot Active | Josh + Keegan (GTM ops) | Reply webhook from sequencer creates pipeline record | Proof/ROI |
| **Proof / ROI Evidence** | Collect and structure pilot outcomes, CoCM billing data, clinical metrics | Context OS knowledge_base | Pilot data, billing records, clinical outcome measures | Case studies, ROI one-pagers, peer reference readiness | Josh + Keegan (GTM ops) | Manual entry post-pilot; Claude Code structures into publishable formats | Messaging Library, Accounts (expansion) |
| **Content / Collateral** | Maintain outbound assets (one-pagers, ROI calculators, integration docs) | Google Drive / Context OS | Messaging Library, Proof/ROI Evidence, product documentation | Versioned collateral tied to persona and subtier | Josh + Keegan (GTM ops) | Claude Code generates drafts; human reviews and publishes | Outreach Sequences |
| **Reporting / Command Center** | Track Day 30/60/90 metrics: emails sent, opens, replies, calls booked, pilots started | Instantly/Smartlead dashboards + Airtable/Pipedrive | Sequencer analytics, CRM pipeline data, call logs | Weekly metric snapshots against cadence targets | Josh + Keegan (GTM ops) | Sequencer dashboards are real-time; Claude Code synthesizes weekly summary | All modules (feedback loop) |

---

## 6. Bill of Systems

### By category

**Data ($160–285/mo + $300–500 one-time)**

| System | Monthly | Annual | Priority |
|--------|---------|--------|----------|
| LeadMagic Essential | $100 | $1,200 | Day 1 |
| Clay Launch | $167–185 | $2,004–2,220 | Day 14 (defer in Lean MVP) |
| CarePrecise | — | $300–500 (one-time) | Day 7 |

**Sales Engagement ($186–235/mo)**

| System | Monthly | Annual | Priority |
|--------|---------|--------|----------|
| Instantly Growth | $37 | $444 | Day 1 |
| HeyReach Growth | $59 | $708 | Day 1 |
| Sales Navigator Core | $90 | $1,080 | Day 1 (start free trial) |

**Email Infrastructure ($99–199/mo + ~$55–88/yr domains)**

| System | Monthly | Annual | Priority |
|--------|---------|--------|----------|
| Zapmail Growth | $99 | $1,188 | Day 1 |
| Porkbun domains | ~$5 | ~$55–88 | Day 1 (if not included with Zapmail) |

**CRM / RevOps ($0–14/mo)**

| System | Monthly | Annual | Priority |
|--------|---------|--------|----------|
| Airtable Free | $0 | $0 | Day 1 |
| Pipedrive Essential (optional) | $14 | $168 | Day 30 (if pipeline UX needed) |

**Phone / Dialer ($0–60/mo)**

| System | Monthly | Annual | Priority |
|--------|---------|--------|----------|
| Trellus Free | $0 | $0 | Day 1 |
| Trellus Power (optional) | $60 | $720 | Day 30 (if volume demands) |
| Quo Starter (alternative) | $15–19 | $180–228 | Day 1 (if dedicated number needed) |

**Research / AI ($200/mo)**

| System | Monthly | Annual | Priority |
|--------|---------|--------|----------|
| Claude Code Max 20x | $200 | $2,400 | Active — already in use |

### Totals

| Tier | Monthly | Annual | One-Time |
|------|---------|--------|----------|
| Lean MVP | ~$490 | ~$5,880 | ~$355–588 |
| Recommended Core | ~$757–775 | ~$9,084–9,300 | ~$300–500 |
| Scale-Ready | ~$986–1,004 | ~$11,832–12,048 | ~$300–500 |

### Cost-saving swaps

| Swap | Saves | Trade-off |
|------|-------|-----------|
| Smartlead Pro instead of Instantly + separate CRM | ~$37–53/mo | Smartlead Pro ($94) includes built-in CRM, eliminating Pipedrive ($14) and potentially Instantly ($37). Net savings depend on whether Smartlead's CRM meets 40+ field needs |
| ScaledMail instead of Zapmail Growth + domains | Simplicity, not cost | $199 vs. ~$104. Costs $95 more but eliminates all domain/inbox decisions. Worthwhile if ops overhead matters more than $95 |
| Trellus Free instead of Quo Starter | $15–19/mo | Lose dedicated business phone number and texting. Trellus Free's 30 dials/week is sufficient for Day 30 volume |
| Skip Clay, manual LinkedIn enrichment | $167–185/mo | Largest single savings. But manual enrichment for 23,700 accounts is unsustainable beyond Phase 1 |

---

## 7. Gaps, Risks, and Questions

### Is this stack too heavy for pre-seed?

The Lean MVP at ~$490/mo is defensible. The Scale-Ready at ~$1,000/mo is aggressive before first revenue. The critical question is: **does the $167-185/mo Clay delta justify itself in the first 30 days, or is it a Day 30-60 purchase?** Recommendation: Lean MVP first, add Clay after validating that LeadMagic alone can't cover enrichment needs.

### Tool overlap

- **Instantly warmup + Zapmail/ScaledMail warmup**: Both include warmup. If using Zapmail pre-warmed inboxes, Instantly's warmup is redundant but harmless. No cost overlap — just configuration to not double-warm.
- **LeadMagic + Clay**: Intentionally layered (primary + waterfall), not duplicative. But if LeadMagic's 97% accuracy covers most contacts, Clay may be underutilized at $167+/mo.
- **Wiza + Sales Nav**: Wiza requires Sales Nav. If LeadMagic is chosen over Wiza, Sales Nav value drops to research-only ($90/mo for research is still defensible but less essential).

### Missing public pricing

| Tool | Status |
|------|--------|
| CarePrecise | No public pricing page. Estimated $300-500 from prior research. Requires direct contact. |
| Trellus credit costs | Credit-based pricing referenced but not publicly detailed beyond plan tiers. |
| ScaledMail per-inbox pricing | Some sources cite $3.50-7/inbox but the main plan is flat $199. Custom quotes may exist. |

### Compliance and procurement risks

- **No PHI in the stack.** All data in this stack is prospect/business data (names, titles, work emails, org affiliations), not patient data. No BAA should be required for any tool listed here.
- **LinkedIn automation risk.** LinkedIn can restrict accounts that use automation tools. HeyReach mitigates with throttling and rotation, but the risk is non-zero. Don't run aggressive automation on Keegan's primary LinkedIn profile — use a dedicated sender account.
- **Email deliverability in healthcare.** Healthcare admin inboxes (especially .gov, large health system domains) may have aggressive spam filtering. The 10-20% open rate assumption from THIRTY_DAY_OFFICE_MANAGER_TARGET needs validation in the first 2 weeks. If open rates are <5%, deliverability infrastructure needs re-evaluation.

### Workflow complexity vs. team capacity

This is a 1-2 person operation running 10+ tools. The design relies on Claude Code as the glue layer — but Claude Code is a research/orchestration tool, not a workflow automation platform. Manual handoffs between systems (sequencer → CRM, enrichment → sequencer, call notes → pipeline) will be friction points until volume justifies automation.

**Specific friction points:**
- Loading enriched contacts from LeadMagic/Clay into Instantly/Smartlead is currently a CSV export/import cycle
- Syncing HeyReach LinkedIn engagement data back to the CRM is manual unless Clay is in the middle
- Call disposition from Trellus/Quo needs manual entry into CRM/pipeline

### Human process vs. software need

- **Messaging hypothesis testing** does not need A/B testing software on Day 1. It needs 5 conversations and a notebook. The Instantly Growth plan without A/B testing is fine for Phase 1.
- **Pipeline management** does not need Pipedrive on Day 1. A 15-row Airtable with deal stages covers the first 10 accounts.
- **Subtier segmentation** is a Claude Code research output, not a software feature. Don't buy a tool to do what a well-structured prompt already does.

### Unvalidated GTM assumptions

The entire stack is built on assumptions that have not yet been tested in market:

1. **Office managers respond to cold outbound.** The operator-first hypothesis is logical but unproven. If office managers don't engage, the stack works fine — but the messaging and targeting strategy changes.
2. **Multichannel (email + LinkedIn) outperforms email-only.** This is generally true in B2B SaaS but unvalidated in healthcare primary care specifically.
3. **The CoCM revenue wedge resonates with operational buyers.** The CoCM estimate engine is a powerful tool — but only if buyers recognize CoCM revenue as a real opportunity, not a theoretical one.
4. **5 conversations in 30 days is achievable with this infrastructure.** The funnel math (500-1000 emails → 50-200 opens → 10-50 replies → 5-10 calls) assumes generic B2B benchmarks. Healthcare may underperform.

---

## 8. Recommendations

### Buy first (Week 1)

| Tool | Action | Cost |
|------|--------|------|
| **Zapmail Growth** | Provision 30 pre-warmed inboxes. DNS/DMARC handled automatically. | $99/mo |
| **Instantly Growth** | Connect Zapmail inboxes. Begin warming (or already pre-warmed). | $37/mo (annual) |
| **Sales Navigator Core** | Start 30-day free trial. Use for buyer research while email warms up. | $0 (trial) |
| **HeyReach Growth** | Start 14-day free trial. Build first LinkedIn sequence. | $0 (trial) |
| **Trellus Free** | Install Chrome extension. Ready for first dials. | $0 |
| **Airtable Free** | Set up account schema from ACCOUNT_SCHEMA_EXTENDED. | $0 |
| **Porkbun** | Register 5 sending domains if not included with Zapmail. | ~$55 one-time |

**Week 1 spend: ~$136/mo + $55 one-time**

### Buy second (Week 2)

| Tool | Action | Cost |
|------|--------|------|
| **CarePrecise** | Purchase healthcare org data. Load into Claude Code for list building. | $300-500 one-time |
| **LeadMagic Basic** | Begin enriching Wave 1 contacts (2,500 credits). | $60/mo |

**Week 2 incremental: ~$60/mo + $300-500 one-time**

### Validate manually before purchasing

| Decision | What to test | When to buy |
|----------|-------------|-------------|
| **Clay** | Can LeadMagic alone get >80% email coverage on Wave 1 list? If yes, defer Clay. If coverage is <60%, add Clay Launch. | Day 14-21 |
| **Pipedrive** | Does Airtable Free feel workable as a pipeline tracker for 10-20 accounts? If painful, add Pipedrive. | Day 30 |
| **Trellus Power** | Are 30 dials/week enough? If you're consistently hitting the cap, upgrade. | Day 30 |
| **Sales Nav** (paid) | Did the free trial generate research value worth $90/mo? If you're building lists primarily from NPPES/CarePrecise, it may not be. | Day 30 |

### Instrument from Day 1

- **Open rates by domain type** (health system .org vs. independent clinic .com vs. personal Gmail) — this tells you if healthcare deliverability is a real problem or a theoretical one
- **Reply rate by persona type** (office manager vs. practice admin vs. clinical director) — this validates or invalidates the operator-first hypothesis
- **LinkedIn acceptance rate** (by subtier and persona) — this tells you if LinkedIn is a viable channel for this market
- **Time from first touch to first call** — this sets realistic expectations for the 30-60-90 cadence

### Revisit after first 10 target accounts

- Whether Clay is needed or LeadMagic standalone is sufficient
- Whether Smartlead's rotation logic would have solved any deliverability issues Instantly couldn't
- Whether a dedicated CRM (Pipedrive) is worth the $14/mo over Airtable
- Whether the 9-subtier segmentation is operationally useful or should be collapsed to 3-4 segments
- Whether the operator-first outreach sequence should shift to clinical-champion-first

---

## Decisions Needed From Kivira

1. **Instantly or Smartlead?** Both start ~$37-39/mo. Instantly has the larger ecosystem; Smartlead has better rotation logic and a built-in CRM. If Smartlead Pro ($94), the CRM question may be moot.

2. **Zapmail or ScaledMail for email infrastructure?** Zapmail Growth ($99) is modular with real Google Workspace accounts. ScaledMail ($199) is flat-rate with 196 inboxes and zero decisions. Zapmail Pro ($299) adds API access for Claude Code provisioning.

3. **LeadMagic or Wiza as primary enrichment?** LeadMagic: credits roll over, no Sales Nav dependency, 19-endpoint API. Wiza: higher accuracy claims (99% vs 97%), requires Sales Nav, credits expire monthly.

4. **Clay now or Clay later?** $167-185/mo is the largest discretionary line item. Recommendation: defer to Day 14-21 after testing LeadMagic standalone coverage.

5. **Trellus or Quo for phone?** Trellus Free (30 dials/week, AI transcription, Chrome extension). Quo Starter ($15-19/mo, dedicated business number, texting). Different tools for different needs — Trellus is a dialer, Quo is a phone system.

6. **How many domains in the first batch?** 5 (conservative, ~$55) or 8-10 (aggressive warmup, ~$88-110)? Zapmail/ScaledMail may include domains — check before purchasing separately.

7. **Sales Navigator: continue after free trial?** At $90/mo, it's the third-largest recurring cost. If LeadMagic is the enrichment tool (not Wiza), Sales Nav's value is buyer research only. Is that worth $90?

8. **CRM timing: when does Airtable stop being enough?** The 40+ field schema fits Airtable. Pipeline management doesn't. At what account volume does the team need a real CRM? 10 accounts? 50? 100?

9. **Budget tier commitment?** Lean MVP (~$490/mo) is sufficient to hit Day 30 targets. Recommended Core (~$757/mo) adds Clay and more inboxes. Scale-Ready (~$986/mo) adds Pipedrive, Trellus Power, Hypergrowth. Which tier matches current runway tolerance?

10. **When to start free trials?** Sales Nav (30 days) and HeyReach (14 days) trials should overlap with email warmup (2-4 weeks). If email infra goes live Week 1, trials should start Week 1 to maximize overlap.

---

*This document is a snapshot as of 2026-04-06. Tool pricing changes frequently. Verify all costs at linked pricing pages before procurement. All pricing reflects publicly available information; where pricing is estimated or unavailable, it is explicitly labeled.*
