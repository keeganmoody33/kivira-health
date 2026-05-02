# Kivira GTM Tech Stack Wish List

**Date:** 2026-04-06
**Context:** Day 1-30 deliverable per Josh Pappas text. Building outbound infrastructure from scratch.
**Related nodes:** [[GTM_30_60_90_EXECUTION_CADENCE]], [[OUTREACH_WAVE_STRUCTURE]], [[THIRTY_DAY_OFFICE_MANAGER_TARGET]], [[ACCOUNT_SCHEMA_EXTENDED]]

---

## Where We're At

Nothing is set up yet. Here's what the repo already defines as infrastructure requirements:

| Requirement | Value | Source |
|-------------|-------|--------|
| Domains needed (cold outbound) | 8-15 | OUTREACH_WAVE_STRUCTURE |
| Daily sends per warmed domain | 50-80 | OUTREACH_WAVE_STRUCTURE |
| Warmup period per domain | 2-4 weeks | OUTREACH_WAVE_STRUCTURE |
| Total campaign emails | 87,000-130,000 | OUTREACH_WAVE_STRUCTURE |
| 30-day email volume (constrained) | 500-1,000 | THIRTY_DAY_OFFICE_MANAGER_TARGET |
| 30-day call target | 5 office managers | THIRTY_DAY_OFFICE_MANAGER_TARGET |
| Account schema fields | 40+ | ACCOUNT_SCHEMA_EXTENDED |
| Free data sources | NPPES, CMS, HRSA, NCQA, PECOS | PUBLIC_DATA_SOURCES_TAM |

---

## The Stack

### 1. Orchestration & Intelligence — Claude Code Max 20x

**Why:** This is the brain. List building, research, account scoring, CoCM estimation, and workflow orchestration all run through Claude Code. Not a nice-to-have — it's the operating system for GTM execution.

| Plan | Monthly Cost | Notes |
|------|-------------|-------|
| **Claude Max 20x** | **$200/mo** | 20x Pro usage. Persistent memory, priority access, extended reasoning. Required for the volume of list building, enrichment orchestration, and multi-step research workflows we're running. |

**Status:** Active. This is the first line item and the most leveraged dollar in the stack.

---

### 2. Email Sequencing / Cold Outbound — Instantly or Smartlead

**Why:** Core sending engine. Sequences, mailbox rotation, open/reply tracking. Everything flows through here.

| Option | Monthly Cost | Key Limits | Notes |
|--------|-------------|------------|-------|
| **Instantly Growth** | $37/mo (annual) / $47/mo (monthly) | 1,000 active leads, 5,000 emails/mo | Unlimited email accounts + warmup included. Bigger community, more tutorials. |
| **Instantly Hypergrowth** | $97/mo | 25,000 active leads, 100,000 emails/mo | A/B testing, advanced analytics. Scale-up tier. |
| **Smartlead Base** | $39/mo | 2,000 contacts, 6,000 emails/mo | Unlimited accounts + warmup. Better auto mailbox rotation. |
| **Smartlead Pro** | $94/mo | 30,000 leads, 150,000 emails/mo | Built-in CRM features — may reduce need for separate CRM. |

**Comparison:**
- Both include unlimited email accounts and built-in warmup on all plans
- Instantly: bigger ecosystem, more integrations, simpler UX
- Smartlead: better rotation logic, built-in CRM, slightly cheaper base tier
- Healthcare deliverability: both support custom tracking domains and DMARC — no major differentiator
- Both integrate with Zapmail and ScaledMail via OAuth

**Decision needed:** Instantly vs. Smartlead. Either works at the ~$37-39/mo entry point.

---

### 3. Email Infrastructure & Inbox Provisioning — ScaledMail or Zapmail

**Why:** Don't manually set up Google Workspace accounts, DNS records, and warmup for 10-30 inboxes. These services provision pre-configured, pre-warmed inboxes with automated SPF/DKIM/DMARC — plug directly into Instantly or Smartlead.

| Option | Monthly Cost | What You Get | Notes |
|--------|-------------|--------------|-------|
| **ScaledMail** | **$199/mo** | 196 inboxes across 4 domains. Up to 11,000 emails/mo. Pre-warmed, pre-configured DNS. | All-in-one flat rate. Massive inbox pool. Domains + inboxes + warmup + DNS bundled. No per-inbox math. |
| **Zapmail Starter** | **$39/mo** | 10 Google Workspace mailboxes. Additional at $3.50/inbox. Automated DNS in <5 min. | More granular. Start small, add inboxes as needed. |
| **Zapmail Growth** | **$99/mo** | 30 mailboxes. Additional at $3.25/inbox. | Sweet spot for Phase 1 scale. |
| **Zapmail Pro** | **$299/mo** | 100 mailboxes. Additional at $3.00/inbox. API access for programmatic provisioning. | Full scale. API lets Claude Code provision inboxes programmatically. |

**Comparison:**

| Factor | ScaledMail | Zapmail |
|--------|-----------|---------|
| Simplicity | One price, everything included | Modular, pay for what you use |
| Phase 1 cost (10-15 inboxes) | $199 (overkill but simple) | $39-99 |
| Scale cost (30+ inboxes) | $199 (still flat) | $99-299 |
| Domains included | Yes (4 domains) | Yes (provisioned with inboxes) |
| Google Workspace | Their own infra | Actual Google Workspace accounts |
| API access | No | Pro plan ($299) |
| Warmup | Pre-warmed | Pre-warmed |

**Recommendation:** Zapmail Growth ($99/mo) for Phase 1 — 30 mailboxes is more than enough, real Google Workspace accounts, and room to grow. ScaledMail if you want zero decisions (flat $199 gets you everything). Zapmail Pro ($299) later if you want API-driven provisioning from Claude Code.

**Note:** With either service, you do NOT need to separately purchase Google Workspace or manage DNS. That's the whole point.

---

### 4. Domain Registration — Porkbun and/or Cloudflare

**Why:** Need 8-15 sending domains separate from kivira.health. These services handle registration; inbox provisioning (ScaledMail/Zapmail) handles everything else.

| Registrar | .com Price | Notes |
|-----------|-----------|-------|
| **Porkbun** | ~$11/year registration + renewal | Transparent pricing — renewal matches registration. Free WHOIS privacy. Bulk-friendly. |
| **Cloudflare Registrar** | ~$10.44/year (.com) | At-cost pricing, zero markup. Best if you're already using Cloudflare for DNS/CDN. 400+ TLDs supported. |

**Important:** If using ScaledMail or Zapmail, they provision domains for you — you may not need to buy domains separately. Check whether your inbox provider includes domain registration or requires you to bring your own.

**If buying separately:**
- Start with 5-8 .com domains: ~$52-88/year (~$4-7/mo)
- Naming: brand variations (kivirahealthteam.com, getkivira.com, kiviraclinical.com, trykivira.com, etc.)
- **Do NOT use kivira.health for cold outbound** — protect the primary domain
- Diversify registrars (don't put all domains at one registrar) to avoid correlated blacklisting

**Recommendation:** Porkbun as primary (transparent, bulk-friendly). Cloudflare for any domains where you want their DNS/CDN stack. Total: **~$4-7/mo** if buying your own.

---

### 5. Data Enrichment — Wiza or LeadMagic (+ Clay for waterfall)

**Why:** Turn NPPES/CMS account lists into contactable leads with verified emails and phone numbers. Claude Code builds the lists; enrichment tools verify and fill contact data.

**Workflow:** Claude Code (list building from NPPES/CMS/public data) → Wiza or LeadMagic (email/phone verification) → Clay (waterfall enrichment for gaps) → Sequencer

| Option | Monthly Cost | Credits | Notes |
|--------|-------------|---------|-------|
| **Wiza Starter** | $49/mo | 100 credits | LinkedIn Sales Nav integration via Chrome extension. 850M+ contacts, 99% email accuracy. Credits don't roll over. **Requires Sales Nav subscription.** |
| **Wiza Email** | $99/mo | 500 emails | Email-only enrichment. Good for email-first outreach. |
| **Wiza Email+Phone** | $199/mo | 500 emails + 500 phones | Full contact enrichment. |
| **LeadMagic Basic** | $59.99/mo | 2,500 credits | Pay-per-result — only charged for valid results. **Credits roll over.** No Sales Nav dependency. |
| **LeadMagic Essential** | $99.99/mo | 10,000 credits | Best value. Email finder at $0.008/credit. Mobile numbers at 5 credits each. |
| **Clay Launch** | $167-185/mo | 2,500 data credits, 15,000 actions | Waterfall enrichment across 75+ providers. Best for filling gaps after Wiza/LeadMagic. |

**Comparison: Wiza vs. LeadMagic**

| Factor | Wiza | LeadMagic |
|--------|------|-----------|
| Pricing model | Fixed credits, expire monthly | Pay-per-result, credits roll over |
| Sales Nav required | Yes (for LinkedIn enrichment) | No |
| Email accuracy | 99% claimed | 97% claimed, 5-layer validation |
| Phone numbers | $199/mo tier | 5 credits each (~$0.04/number) |
| API | Yes | Yes (documented at leadmagic.io/docs) |
| Best for | LinkedIn-first prospecting | Volume enrichment without Sales Nav dependency |

**Recommendation:** LeadMagic Essential ($99.99/mo) as primary enrichment — no Sales Nav dependency, credits roll over, pay-per-result means no waste. Add Clay Launch ($167-185/mo) as the waterfall layer for contacts LeadMagic can't find. Wiza is the pick if you're already committed to Sales Nav.

**One-time:** CarePrecise ($300-500) for healthcare org + clinician + affiliation data (already identified in PUBLIC_DATA_SOURCES_TAM).

---

### 6. CRM / Pipeline Management

**Why:** Track accounts, contacts, deals, outreach status. ACCOUNT_SCHEMA_EXTENDED defines 40+ fields.

| Option | Monthly Cost | Notes |
|--------|-------------|-------|
| **HubSpot Free** | $0 | 1,000 contacts, **10 custom properties total** — won't fit 40+ field schema without Professional ($90/mo). Ecosystem is great but free tier is a trap. |
| **Airtable Free** | $0 | Unlimited fields, 1,000 records. Pro ($20/mo) gets 50,000 records. Schema-flexible. No pipeline UX — it's a database. |
| **Pipedrive Essential** | $14/user/mo | Unlimited custom fields. 3,000 open deals. Real pipeline UX. |
| **Smartlead built-in CRM** | $0 (included in Pro) | If Smartlead Pro is the sequencer, CRM is bundled. Limited vs. dedicated CRM. |

**Note:** If Smartlead Pro is chosen as sequencer, its built-in CRM may be sufficient for Phase 1, deferring a dedicated CRM decision to Day 30-60.

---

### 7. Phone / Dialer

**Why:** Office managers answer phones. 30-day target is 5 conversations.

| Option | Monthly Cost | Notes |
|--------|-------------|-------|
| **Google Voice** | $0 (personal) / $10/user (business) | Basic. No CRM integration. Works for 5 calls. |
| **Quo (OpenPhone) Starter** | $15/user/mo (annual) / $19/mo (monthly) | Local number, unlimited US/CA calling/texting, voicemail transcription, AI features. |
| **Quo Business** | $23/user/mo (annual) | HubSpot/Salesforce integration, call recording, analytics. |

**Recommendation:** Google Voice for minimum. Quo Starter ($15/mo) if you want texting + AI transcription.

---

### 8. LinkedIn — Sales Navigator + HeyReach

**Why:** LinkedIn is a primary channel alongside email. Sales Nav for research, lead lists, and buyer validation. HeyReach for automated LinkedIn outreach (connection requests, messages, InMail sequences) that runs in parallel with email sequences.

#### Sales Navigator

| Plan | Monthly Cost | Notes |
|------|-------------|-------|
| **Sales Navigator Core** | $99/mo (monthly) / $90/mo (annual) | Advanced search, lead lists, InMail credits. 30-day free trial. Also required for Wiza if chosen as enrichment tool. |

#### HeyReach (LinkedIn Automation)

| Plan | Monthly Cost | Notes |
|------|-------------|-------|
| **Growth** | $79/mo (monthly) / $59/mo (annual) | 1 LinkedIn sender seat. Automated connection requests, messages, profile visits, InMail sequences. |
| **Agency** | $799/mo | Up to 50 LinkedIn accounts. $15/account at scale. Overkill for now. |

**What HeyReach does:**
- Automates LinkedIn outreach sequences (connect → view profile → message → follow-up)
- Rotates across multiple LinkedIn sender accounts (if scaling later)
- Tracks acceptance rates, reply rates, meeting conversions
- Charges per LinkedIn sender, not per user — whole team can manage from one dashboard
- 14-day free trial (3 seats, no credit card)

**Why both:** Sales Nav finds the right people. HeyReach automates the outreach to them. Email sequences (Instantly/Smartlead) and LinkedIn sequences (HeyReach) run as parallel channels hitting the same prospect list — multichannel increases reply rates significantly vs. email-only.

**Combined LinkedIn cost:** $99 + $79 = **$178/mo** (monthly) or $90 + $59 = **$149/mo** (annual)

---

### 9. Workflow Automation

**Why:** Connect CRM ↔ sequencer ↔ enrichment. Defer to Day 30-60.

| Option | Monthly Cost | Notes |
|--------|-------------|-------|
| **Zapier Free** | $0 | 100 tasks/mo, 5 Zaps |
| **Make** | $9/mo | 10,000 ops/mo. More flexible. |

**Note:** Claude Code handles most orchestration. Zapier/Make only needed for automated triggers between systems (e.g., new reply → create CRM record).

---

### 10. Analytics & Tracking

Covered by sequencer built-in dashboards + Calendly Free for meeting booking + PostHog (already connected).

---

## Monthly Burn Summary

### Minimum Stack

Get sending on email + LinkedIn. Manual enrichment. Claude Code does the heavy lifting.

| Category | Tool | Monthly Cost |
|----------|------|-------------|
| Orchestration | Claude Code Max 20x | $200 |
| Sequencer | Instantly Growth or Smartlead Base | $37-39 |
| Email Infra | Zapmail Starter (10 inboxes) | $39 |
| Domains | Porkbun (5 .com, if not included with Zapmail) | ~$5 |
| Enrichment | LeadMagic Basic (2,500 credits) | $60 |
| LinkedIn | Sales Navigator Core (annual) | $90 |
| LinkedIn Automation | HeyReach Growth (annual) | $59 |
| CRM | Airtable Free | $0 |
| Phone | Google Voice | $0 |
| Meetings | Calendly Free | $0 |
| **Total** | | **~$490-492/mo** |

Plus one-time: CarePrecise $300-500, domain registration ~$45-55

### Recommended Lean Stack

Core automation on both channels. Clay fills enrichment gaps. Real phone.

| Category | Tool | Monthly Cost |
|----------|------|-------------|
| Orchestration | Claude Code Max 20x | $200 |
| Sequencer | Instantly Growth or Smartlead Base | $37-39 |
| Email Infra | Zapmail Growth (30 inboxes) | $99 |
| Domains | Porkbun/Cloudflare (if needed) | ~$5 |
| Enrichment | LeadMagic Essential (10K credits) | $100 |
| Enrichment (waterfall) | Clay Launch | $167-185 |
| LinkedIn | Sales Navigator Core (annual) | $90 |
| LinkedIn Automation | HeyReach Growth (annual) | $59 |
| CRM | Airtable Free or Pipedrive | $0-14 |
| Phone | Quo Starter | $15 |
| Meetings | Calendly Free | $0 |
| **Total** | | **~$772-811/mo** |

Plus one-time: CarePrecise $300-500

### Full Wish List

Everything running. Upgraded sequencer. ScaledMail for simplicity. Full enrichment stack.

| Category | Tool | Monthly Cost |
|----------|------|-------------|
| Orchestration | Claude Code Max 20x | $200 |
| Sequencer | Instantly Hypergrowth or Smartlead Pro | $94-97 |
| Email Infra | ScaledMail (196 inboxes, 4 domains) | $199 |
| Domains | Included with ScaledMail | $0 |
| Enrichment | LeadMagic Essential | $100 |
| Enrichment (waterfall) | Clay Launch | $167-185 |
| LinkedIn | Sales Navigator Core (annual) | $90 |
| LinkedIn Automation | HeyReach Growth (annual) | $59 |
| CRM | Pipedrive Essential | $14 |
| Phone | Quo Starter | $15 |
| Meetings | Calendly Standard | $10 |
| Automation | Make | $9 |
| **Total** | | **~$957-978/mo** |

Plus one-time: CarePrecise $300-500

---

## Implementation Sequencing

| Timeframe | Action | Tools to Procure |
|-----------|--------|-----------------|
| **Week 1** | Set up inbox provisioning (ScaledMail or Zapmail). Domains, DNS, warmup handled automatically. | ScaledMail or Zapmail |
| **Week 1** | Register any additional domains if needed. | Porkbun / Cloudflare |
| **Week 1-2** | Connect inboxes to sequencer. Warmup begins (or already pre-warmed). | Instantly or Smartlead |
| **Week 2** | Purchase CarePrecise. Build Wave 1 target list in Claude Code from NPPES + CarePrecise + public data. | CarePrecise (one-time) |
| **Week 2-3** | Enrich contacts via LeadMagic (or Wiza). Fill gaps with Clay waterfall. Load into sequencer. | LeadMagic, Clay (if budget allows) |
| **Week 3** | Launch first sequences. Begin dialing office managers. | Quo Starter (if budget allows) |
| **Week 4** | Monitor deliverability, reply rates. Iterate messaging per MESSAGING_HYPOTHESIS_DISCIPLINE. | — |
| **Day 30** | Checkpoint: 5 calls hit? Review enrichment ROI. Decide on scale-up tools. | Evaluate: Sales Nav, upgraded sequencer, Clay |

---

## Decisions Needed (for Josh + Keegan)

1. **Sequencer:** Instantly vs. Smartlead?
2. **Email Infra:** ScaledMail ($199 flat, massive) vs. Zapmail ($39-99, modular)?
3. **Enrichment primary:** LeadMagic (credits roll over, no Sales Nav dependency) vs. Wiza (higher accuracy claims, Sales Nav-powered)?
4. **Clay:** Add at $167-185/mo for waterfall enrichment, or defer and rely solely on LeadMagic/Wiza?
5. **Budget tier:** Minimum (~$490/mo), Lean (~$772-811/mo), or Full (~$957-978/mo)?
6. **Timing:** Start Sales Nav + HeyReach 30-day free trials now (Week 1) to overlap with email warmup period?

---

## What This Document Does NOT Cover

- **Sequence copy / email templates** → see MESSAGING_HYPOTHESIS_DISCIPLINE, COCM_OUTREACH_SEQUENCING
- **Who to target and in what order** → see OUTREACH_WAVE_STRUCTURE, GTM_TIER_ARCHITECTURE_9_SUBTIERS
- **TAM list building methodology** → see PUBLIC_DATA_SOURCES_TAM, TAM_DEDUP_METHODOLOGY
- **CoCM revenue estimates for outreach** → see COCM_PUBLIC_ESTIMATE_ENGINE_V2

---

## Sources

- [Instantly.ai Pricing](https://instantly.ai/pricing)
- [Instantly.ai Pricing Breakdown 2026](https://coldemailkit.com/tools/instantly)
- [Smartlead Pricing](https://www.smartlead.ai/pricing)
- [Smartlead Pricing Breakdown 2026](https://coldemailkit.com/tools/smartlead)
- [ScaledMail Pricing](https://www.scaledmail.com/pricing)
- [ScaledMail Review & Features](https://www.beanstalkconsulting.co/playbooks/scaledmail-review-features)
- [Zapmail Pricing & Features](https://zapmail.ai)
- [Zapmail Review 2026](https://coldemailkit.com/tools/zapmail)
- [Porkbun Domain Pricing](https://porkbun.com/products/domains)
- [Cloudflare Registrar](https://www.cloudflare.com/products/registrar/)
- [Cloudflare Domain Pricing Tracker](https://cfdomainpricing.com/)
- [Clay Pricing 2026](https://www.clay.com/pricing)
- [Clay Pricing Changes March 2026](https://www.cleanlist.ai/blog/2026-03-12-clay-pricing-changes-2026)
- [Wiza Pricing](https://wiza.co/pricing)
- [Wiza Review 2026](https://derrick-app.com/en/wiza-pricing/)
- [LeadMagic Pricing](https://leadmagic.io/pricing)
- [LeadMagic Review 2026](https://syncgtm.com/blog/leadmagic-review)
- [HubSpot Free CRM Limitations 2026](https://claritysoft.com/hubspot-free-plan-limitations/)
- [Quo (OpenPhone) Pricing](https://www.quo.com/blog/quo-pricing/)
- [LinkedIn Sales Navigator Plans](https://business.linkedin.com/sales-solutions/compare-plans)
- [HeyReach Pricing](https://www.heyreach.io/pricing)
- [HeyReach Overview 2026](https://www.salesforge.ai/directory/sales-tools/heyreach)
- [Claude Code Pricing 2026](https://claude.com/pricing)
- [Google Workspace Reseller Pricing 2026](https://leadsmonky.com/google-workspace-reseller-pricing-2026/)
