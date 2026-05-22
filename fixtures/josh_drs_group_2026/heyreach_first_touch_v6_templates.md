# HeyReach sequence copy — first DM after accept (v6)

**Canonical rules:** `knowledge_base/methodology/KIVIRA_FIRST_TOUCH_LINKEDIN_PLAYBOOK.md`

**Scope:** Paste into HeyReach as the **first message after connection is accepted**. Connection request text is separate (keep short; no "Hi," no em/en dashes).

**Campaigns (create PAUSED):** one per cluster — IDs in `josh_campaign_ids.json`

| Campaign name | Cluster | ~Leads |
|---------------|---------|--------|
| `Josh-Pilot-ClusterA-Provider-20260522` | A | see dry-run |
| `Josh-Pilot-ClusterB-VBC-20260522` | B | |
| `Josh-Pilot-ClusterC-CareMgmt-20260522` | C | |
| `Josh-Pilot-ClusterD-Partnership-20260522` | D | |
| `Josh-Pilot-ClusterE-Founder-20260522` | E | |

**Titling:** HeyReach cannot branch Dr. vs first name in one template. Use `{{firstName}}` in automation; for MD/DO accepts, edit to `Dr. {{lastName}},` before send or use list export + manual pass on physician rows.

---

## Optional connection request (not in playbook; keep minimal)

Generic (all clusters), under 200 characters:

> Working on primary-care mental-health decision support, backed by Antler and Wellstar Catalyst. Curious if the BH workflow theme shows up on your side. Open to connect?

---

## A. Provider workflow (1A / 1B / 3A)

{{first_name_or_dr}},

I'm working w/ Kivira.health, a mental-health clinical decision support tool for primary care, backed by Antler and Wellstar Catalyst.

The few physicians I've spoken w/ say mental health is either case-and-point for the visit, or documentation feels disconnected from the care actually provided. It's a tough one to nail down across timelines, I can only imagine. What we're building is meant to improve day-to-day for clinicians like yourself: documenting the subtleties and nuance, flagging when something might need an extra look from a BH standpoint, making documentation easier.

Would you be open to jumping on a call, letting us demo, and telling us where you can imagine this fitting into your future day-to-day, and where it just wouldn't work?

Our founder Maria will demo. We'd benefit from your feedback.

Keegan

---

## B. VBC / risk (1C / 2A / 3C)

{{first_name_or_dr}},

I'm working w/ Kivira.health, a mental-health clinical decision support tool for primary care, backed by Antler and Wellstar Catalyst.

The quality and risk leaders I've spoken w/ say the BH signal often doesn't make it from the visit into the chart, which is exactly where RAF accuracy, HEDIS, and Stars actually live or die. I can only imagine how that compounds at network scale. What we're building is meant to tighten that gap: documenting subtleties and nuance at the point of care, flagging coding-relevant BH signal so it reaches the chart, making the downstream performance story cleaner.

Would you be open to jumping on a call, letting us demo, and telling us where you can imagine this fitting into your future day-to-day, and where it just wouldn't work?

Our founder Maria will demo. We'd benefit from your feedback.

Keegan

---

## C. Care coordination (2C)

{{first_name_or_dr}},

I'm working w/ Kivira.health, a mental-health clinical decision support tool for primary care, backed by Antler and Wellstar Catalyst.

The care management leaders I've spoken w/ say the PCP-to-care-manager handoff is often lossy, what gets surfaced in the visit doesn't always reach the team owning follow-up. I can only imagine how often you inherit a chart that doesn't tell the whole story. What we're building is meant to be the BH triage and escalation layer between screening and your team's workflow: documenting the subtleties, flagging what needs follow-up, making the handoff land.

Would you be open to jumping on a call, letting us demo, and telling us where you can imagine this fitting into your future day-to-day, and where it just wouldn't work?

Our founder Maria will demo. We'd benefit from your feedback.

Keegan

---

## D. Partnership / channel (2B)

{{first_name_or_dr}},

I'm working w/ Kivira.health, a mental-health clinical decision support tool for primary care, backed by Antler and Wellstar Catalyst.

The partnership and product leaders I've spoken w/ at platforms like {{company}} say the BH workflow piece comes up in nearly every engagement and rarely has a clean answer. I can only imagine how that lands when you're trying to support member groups at scale. What we're building is an in-EHR CDS layer, no custom build required, and there's likely a shape where Kivira embeds through what you've already built rather than selling to each member group standalone.

Would you be open to jumping on a call to explore the partnership surface, letting us demo, and telling us where you can imagine this fitting and where it just wouldn't?

Our founder Maria will demo. We'd benefit from your feedback.

Keegan

---

## E. Founder / peer / unclear

{{first_name_or_dr}},

I'm working w/ Kivira.health, a mental-health clinical decision support tool for primary care, backed by Antler and Wellstar Catalyst.

Curious how {{company}} is approaching this surface. The founders I've spoken w/ at this stage say peer feedback is one of the highest-signal inputs they get, and I can only imagine the same is true on your end. There might be a shape worth comparing notes on, or you might point me toward someone in your network who'd be into this.

Would you be open to jumping on a call, letting us demo, and telling us where you can imagine this fitting and where it just wouldn't?

Our founder Maria will demo. We'd benefit from your read.

Keegan
