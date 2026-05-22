# Josh pilot — HeyReach campaign wiring (v6)

**Purpose:** Route list `686808` into five **PAUSED** cluster campaigns aligned with [[KIVIRA_FIRST_TOUCH_LINKEDIN_PLAYBOOK]]. Go-live requires Keegan approval.

## Architecture

| Cluster | UI campaign name | Playbook template |
|---------|------------------|-------------------|
| A | `Josh-Pilot-ClusterA-Provider-20260522` | Provider workflow |
| B | `Josh-Pilot-ClusterB-VBC-20260522` | VBC / risk |
| C | `Josh-Pilot-ClusterC-CareMgmt-20260522` | Care coordination |
| D | `Josh-Pilot-ClusterD-Partnership-20260522` | Partnership / channel |
| E | `Josh-Pilot-ClusterE-Founder-20260522` | Founder / peer / unclear |

Classifier: `tam_builder/josh_pilot/first_touch_cluster.py` (used by `scripts/wire_josh_heyreach_campaigns.py`).

**Not message_lane.** Lane export remains in CSV for audit; routing uses role/cluster rules from the playbook.

## Scripts

| Step | Command |
|------|---------|
| List loaded | `python3 scripts/load_josh_heyreach_list.py --list-id 686808` |
| Dry-run cluster split | `python3 scripts/wire_josh_heyreach_campaigns.py` |
| Load campaigns | `--commit` after IDs in `josh_campaign_ids.json` |
| Go live | `go_live_approved: true` then `--go-live` or UI start |

## Go-live gate

1. `go_live_approved` in JSON
2. Sender `192406` active
3. v6 templates pasted; escape-hatch CTA intact
4. MD/DO accepts: plan manual `Dr. Lastname` where HeyReach only has `{{firstName}}`

## Related

- [[JOSH_PILOT_LIST_MOTION_2026]]
- [[KIVIRA_OUTBOUND_MESSAGE_PATTERN_V6_2026_05_20]] (Wave 1 warm follow-up cohort; playbook is canonical for new accepts)
- [[heyreach-mcp-load-runbook]] (Wave1 persona campaigns, separate)
