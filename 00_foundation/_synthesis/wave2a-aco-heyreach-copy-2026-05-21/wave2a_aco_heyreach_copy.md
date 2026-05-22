# Wave 2A HeyReach Copy — ACOs (Sub-tier 2A) — DRAFT

**Status:** Draft. Promote to `00_foundation/messaging/wave2a_aco_heyreach_copy.md` only after human review per CLAUDE.md hard rule #1.

**Audience:** Named decision-makers at MSSP / REACH ACOs, ACO-IPAs, and health-system-affiliated ACOs (50K to 500K attributed lives). Not single-site practices, not payers, not vendors.

**Guardrails (all touches):**

- Product is **clinical decision support (CDS)**. Not autonomous diagnosis. Align with public/legal framing per `[[CDS_NOT_DIAGNOSIS_FRAMING]]`.
- No unsourced ROI %. No claimed bps of Stars lift. No specific savings figures unless tied to a public source.
- Pain anchors: BH-driven medical spend (ED + admits), Stars/HEDIS depression follow-up performance, network leakage on BH referrals, attribution-protecting workflows.
- ACO framing rule: Kivira influences total cost of care via PCP-side BH workflow (where the visit actually happens). It is not a new care-management product, not a referral marketplace, not autonomous diagnosis.

**Character targets:** Connection note ≤200 characters. First DM 600 to 800 characters. Soft CTA (15-minute call). No calendar link.

**Voice rules (per project memory):** No "Hi" opener. No em-dashes. No "folks". Periods and commas only. Role language, not generational filler.

---

## 1. Operational Owner

**Primary persona titles (per `[[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]]` 2A):** VP Population Health, Director of Population Health, Director of Care Coordination, Director of Network Performance, Risk Operations Leader, Director of Value-Based Operations.

**Primary theme:** Quality measure attainment and network-side workflow.

### Connection request

> ACO ops + behavioral health is the messy intersection. Stars/HEDIS depression measures rarely get won at the network level. Open to compare notes?

_(149 chars)_

### First DM

> Thanks for connecting. I work with ACOs on the part of the depression measure that gets won or lost inside the PCP visit, not at the care-management layer.
>
> A lot of networks your size have the right BH partnership stack, but the screening and follow-up loop still bombs because the PCP can't close the measure during a 15-minute visit. We're clinical decision support that sits in the existing workflow. No new care-management product, no autonomous diagnosis.
>
> If any of that lines up with where your network is on the BH measure set, happy to do a 15-minute pass. If a different team owns that work at your ACO, a pointer there would help.

---

## 2. Clinical Champion

**Primary persona titles:** CMO, VP Medical Affairs, Medical Director Population Health, Physician Executive VBC, Chief Clinical Officer, Medical Director Quality, VP Clinical Affairs.

**Primary theme:** Defensible clinical strategy. Medical-staff durability.

### Connection request

> BH-related ED utilization in an ACO is a line item that resists every standard intervention. Curious how your network is approaching the workflow side. Open to connect?

_(167 chars)_

### First DM

> Appreciate the add. Focused on how PCPs in ACO networks get instrument-backed BH decision support inside the visit, so the clinical story holds up in med staff and quality committee, not just the sales conversation.
>
> The angle I care about: transparent methodology, bounded outputs, no autonomous diagnosis framing. The medical staff signs off because the workflow is clinically defensible, not because someone promised a number.
>
> If you're the right person to pressure-test the clinical approach with, I'd value 15 minutes. If not, a pointer to your ambulatory or population-health clinical lead would help.

---

## 3. Economic Buyer

**Primary persona titles:** CEO, President, CFO, COO, VP Network Performance, SVP Clinical Affairs, Executive Director.

**Primary theme:** Total cost of care and Stars/MSSP bonus.

**Sequencing rule:** Do not lead cold. Use after warm signal at the same account, or after `Operational Owner` / `Clinical Champion` engagement at the parent system.

### Connection request

> Leading an ACO right now means BH-driven medical spend hits both your loss ratio and your Stars bonus. Worth comparing notes if you're rethinking the network-side approach.

_(174 chars)_

### First DM

> Thanks for connecting. I'll skip the cold ROI thread since that's not how ACO finance actually works.
>
> What I would compare notes on: ACOs of your size typically have BH-related spend leakage and a depression follow-up Stars gap that sit on the same PCP-visit workflow. We're decision support inside that visit, not a care-management product overlay, not a referral marketplace.
>
> Not asking for a pricing conversation. If your ACO already has someone owning the BH side of total cost of care, a pointer there is the right move. If that work is still split across pop-health and ambulatory clinical leadership, 15 minutes to align on how you're thinking about it would be useful.

---

## 4. Technical Gatekeeper

**Primary persona titles:** Director of Analytics, VP Data & Analytics, Interoperability Lead, Director of Reporting, Health IT Director, Director of Clinical Analytics, CIO, CMIO.

**Primary theme:** Integration sanity. Security posture. Vendor risk.

### Connection request

> Health IT at an ACO means evaluating every BH workflow tool that promises to ride your FHIR layer without a custom build. Most don't. Open to connect?

_(151 chars)_

### First DM

> Thanks for the connection. I know your inbox is full of vendors promising FHIR fairy tales and Epic deep links that die in security review.
>
> Practical question for an ACO-side stack: when clinical asks for "BH support inside the PCP visit," how do you keep it inside the existing auth, audit, and release governance? Our approach: minimal integration surface, in-EHR CDS, clear data boundary, no patient data leaving the EHR for a vendor cloud.
>
> If that's the bar on your side, 15 minutes to compare notes would be useful. No implementation deep-dive unless you want one.

---

## 5. BH / Quality Influencer

**Primary persona titles:** Director of Behavioral Health Programs, VP Quality Operations, Director of Quality Improvement, Quality Performance Director, Director of Clinical Quality Programs, Behavioral Health Network Director, Stars Program Director.

**Primary theme:** Network-level BH measure ownership. The "lever and outcome don't sit in the same building" pattern.

### Connection request

> Owning the BH measure set across an ACO is the rare role where the lever and the outcome don't sit in the same building. Curious how you're handling it.

_(154 chars)_

### First DM

> Thanks for connecting. People in your role usually own the uncomfortable overlap: BH-related quality measures the network is graded on, and PCP visits where those measures actually move.
>
> What I'd be interested in: whether your network measures closure (completed follow-up, documented handoff, intervention recorded) or just screening rates. The Stars and HEDIS gap usually lives in the closure step, not the screen.
>
> Happy to keep this exploratory unless you're actively evaluating tools. If a demo ever makes sense, ops and clinical in the room is the right shape, and our founder Maria would join.

---

## Variable inserts (optional HeyReach custom fields)

| Variable | Source |
|---|---|
| `subtier` | Always `2A` for this wave |
| `persona_bucket` | From `fixtures/aco_persona_ranked.csv` `persona_bucket` column |
| `aco_name` | From `companyName` |

---

## Notes on why this is different from `wave1a_heyreach_copy.md`

Wave 1A copy is anchored on the **PCP-visit workflow load**: PHQ-9 documentation in a 15-minute visit, care-manager doc burden. The buyer at a 1A mid-market PCP group is operationally close to the visit and feels that load directly.

Wave 2A copy is anchored on **network-level total cost of care and quality measure attainment**. The 2A buyer (ACO VP Pop Health, CMO, etc.) is one layer removed from the visit. Their pain is the aggregate across a network, not any single PCP encounter. The PHQ-9-in-the-visit framing reads as too tactical for them.

Do not reuse the 1A copy on 2A targets. The Wave 1 zero-accept result on the 2A pool inside `Wave1-OperationalOwner` (HeyReach campaign 416316) is at least partly attributable to mismatched pain anchoring.

---

## Open questions before promotion

1. Should the Operational Owner first DM cite Antler / Wellstar Catalyst, or hold those for the demo conversation? Wave 1A copy holds them. The Josh-annotation v7 follow-up copy uses them up front. Different contexts.
2. Founder Maria mention: included only in the BH/Quality DM here. Could be added to Op Owner and Clinical Champion if testing shows benefit.
3. CTA wording: "15 minutes" repeated in every DM is intentional (familiarity / signal of low ask). Consider one variant per persona if testing shows fatigue.
4. Sequencing rule for Economic Buyer (do not lead cold): should the HeyReach campaign exclude econ-buyer rows from the first-touch list, or include them with this softer DM?

---

**Created:** 2026-05-21 (draft)
**Sender on send:** Keegan (`keeganmoody33@gmail.com` LinkedIn account, same as Wave 1)
**Related:** [[PERSONA_TITLE_DICTIONARY_BY_SUBTIER]] · [[ORG_TYPE_BUYER_MAP_COCM]] · [[ACO_BLITZ_2026_05_W2_PLAN]] · [[GTM_TIER_ARCHITECTURE_9_SUBTIERS]] · [[CDS_NOT_DIAGNOSIS_FRAMING]]
