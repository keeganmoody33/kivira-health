---
name: KIVIRA_OUTBOUND_MESSAGE_PATTERN_2026_05_12
description: Canonical 5-paragraph LinkedIn DM pattern for warm follow-up to accepted connections — domain-led, named-funder social proof, role-specific value-prop, demo-with-founder beat, two-path ask close.
domain: methodology
node_type: pattern
status: validated
last_updated: 2026-05-12
tags:
  - methodology
  - gtm-motion
  - outbound
  - linkedin-outreach
  - source-internal-doc
topics:
  - gtm-motion
  - workflow
  - discovery-calls
related_concepts:
  - "[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]"
  - "[[GTM_TIER_ARCHITECTURE_9_SUBTIERS]]"
  - "[[OUTREACH_BASELINE_METRICS]]"
  - "[[KIVIRA_COMPANY_PROFILE_2026_05_11]]"
  - "[[DEMO_FIRST_OUTBOUND_STRATEGY]]"
source:
  type: internal-doc
  file: "00_foundation/_synthesis/josh-followup-2026-05-11/messages-josh-preview.md"
  date: "2026-05-12"
---

# Kivira outbound message pattern (v5, 2026-05-12)

The canonical LinkedIn DM shape for warm follow-up after a connection accept. Five paragraphs, ~50 words total, no greeting, no thanks-for-connect. Optimized for sales-facing recipients who already know we're a real person (they accepted our connection) and now need to know what we are, why we matter to them, and what we're asking.

[VERIFIED: Pattern crystallized through 5 revision passes with the Kivira GTM lead on 2026-05-11, applied to the 10-person Wave 1 in-scope follow-up batch.]

## The shape

```
Inside Kivira.health: mental-health clinical decision support for primary care,
backed by Antler and funded by Wellstar Catalyst.

{1-2 sentences: role-specific value-prop tied to the recipient's sub-tier pain.}

Demo would be with our founder.

Your read on this, or direction toward whoever at {company} owns this surface.

Keegan
```

## Why each beat is load-bearing

### Beat 1: Domain-led identification
*"Inside Kivira.health: mental-health clinical decision support for primary care, backed by Antler and funded by Wellstar Catalyst."*

- **Leads with the URL** (Kivira.health) so the recipient can click through and self-orient before deciding to reply. The colon construction gives them a one-line definition they can scan in 2 seconds.
- **Named funder beats vague phrasing.** "Backed by Antler and funded by Wellstar Catalyst" beats "backed by Antler and major healthcare systems" because (a) named entities are verifiable, (b) a healthcare-system funder is sub-tier-relevant social proof for healthcare buyers, (c) it answers the unspoken "are you real?" question without name-dropping medical-board members the recipient doesn't know.
- **No mention of "I'm running GTM at Kivira"** — that framing is about the sender's role, not the recipient's interest.

### Beat 2: Role-specific value-prop
*"For {their org-type} like {their company}, we close {specific pain that lands on their sub-tier metrics}."*

- One or two short sentences max. Must name the recipient's actual sub-tier pain, not Kivira's generic capabilities.
- Reference [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]] for the role-to-pain mapping per sub-tier.
- Examples from Wave 1:
  - 1C VBC PCP: "we close the BH diagnostic gap that lands on HEDIS and RAF"
  - 1A multi-site PCP: "our workflow runs inside the visit and helps clinicians screen, document, and act — no new FTEs"
  - 3C regional payer: "we close the gap between what network PCPs document and what your members need for Stars, HEDIS, and risk adjustment on the MA book"

### Beat 3: Demo would be with our founder
*"Demo would be with our founder."*

- Stands alone on its own line. Never buried.
- Adds founder-level credibility to the demo ask without naming the founder (Maria T Carmona, MBA) explicitly. Naming becomes a conversational-delta the sender can add at send time if appropriate.
- Implicit signal: this isn't a vendor sales call; it's a co-founder conversation.

### Beat 4: Two-path close
*"Your read on this, or direction toward whoever at {company} owns this surface."*

- **Two paths in one sentence:** the recipient either gives their own read OR forwards us to the right operator at their org. The "or direction toward whoever owns this surface" is the unlock — most recipients pick door #2 because forwarding is lower-cost than commit-to-meeting.
- **No "We'd love"** hedge. Statement form, not question form. Direct without being demanding.
- **No "If your week's packed"** softener. The two paths are already a soft alternative; doubling the softness reads like padding.

### Beat 5: Single-name sign-off
*"Keegan"*

- No em-dash before the name (em-dashes get cut throughout the message body too).
- No "Best," / "Cheers,". Just the name. LinkedIn shows the sender's full name in the avatar header anyway.

## Anti-patterns (do not use)

- **"Hi {firstName}," greeting** — drop. We already exchanged greetings on the connection accept.
- **"Thanks for connecting"** — HeyReach already sent that on Keegan's behalf when the connection request was accepted.
- **"I'm running GTM at Kivira"** — sender-centric framing; replace with domain-led identification.
- **"Curious if you'd be open to a short exploratory call"** — templated softness that telegraphs sales. The two-path close subsumes this ask.
- **"If your week is too packed, no problem — happy if you can point us to whoever at {company} owns this surface."** — too long, too soft. Compress to the two-path single sentence.
- **Medical-board name-dropping** (Nemeroff, Akiki, etc.) — was tested in v1-v3 drafts but adds length without proportional lift. The named-funder line is stronger social proof for sales-facing recipients. The medical board names are on Kivira.health/team for recipients who click through.
- **Em-dashes anywhere in the message** — replace with periods or commas. The pattern's voice is direct, not stylized.
- **Calendly links** — read as automated cadence. If the recipient says yes to a call, propose two specific times in the next message.
- **Sub-tier labels in the message body** ("1C", "Tier 2A") — these are internal-only. Never expose them.

## Sender attribution

Pattern designed for sends from **Keegan's LinkedIn account** (keeganmoody33), where Wave 1's 58 accepts were collected. If sender ever changes:

- The "Keegan" sign-off must change to match the actual sender.
- The "Demo would be with our founder" line still works as long as the actual sender is not the founder. If a founder ever runs outbound from their own account, replace with "Happy to do the demo myself" or similar.

## Channel applicability

- **Primary:** LinkedIn DM follow-up to accepted connection requests (the use case this pattern was built for).
- **Likely extends to:** cold email if the sender + subject-line context is established. The 5-beat structure is channel-agnostic; only the greeting omission is LinkedIn-specific.
- **Does not apply to:** initial connection-request copy (different constraint: ~300 characters max, no domain link possible, no Beat 1 colon construction).

## When to deviate

- **Reply already in thread:** the recipient already replied substantively. The pattern is built for accepted-but-not-replied connections. If they've already said something, lead with a response to their content, then use beats 2-4 inline.
- **Founder-to-founder context:** replace Beat 1 with "Inside Kivira.health: mental-health clinical decision support for primary care. {Brief comparison signal between your company and theirs.}" and skip the funder line (founders care less about your funder, more about your product).
- **Plan-side (3C) recipient:** Beat 3 ("Demo would be with our founder") can be reinforced with "Carol Alter (medical board, payer-side reimbursement expertise) often joins payer demos" — only if it's true on the send day.

## Production data

- First sent: Wave 1 in-scope follow-up batch starting 2026-05-12.
- Cohort: 10 LinkedIn accepts (1A: 1, 1C: 3, 2B: 2, 2C: 2, 3C: 2) — see `00_foundation/_synthesis/josh-followup-2026-05-11/`.
- Reply-rate target: ≥40% (significantly above the 14% post-launch reply rate observed on the initial outbound campaign copy in Wave 1, because these are warm responses to people who already chose to connect).
- First measurable read: 2026-05-19 (7 days after first batch sent).

## Refresh cadence

Re-evaluate this pattern monthly or after each Wave's send-cycle, whichever is sooner. If reply-rate falls below 30% at a comparable volume, A/B test the pattern against alternatives. Mint a successor node `KIVIRA_OUTBOUND_MESSAGE_PATTERN_<next-date>` rather than overwriting this one (preserves the version chain for what worked when).
