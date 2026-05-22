# Josh pilot HeyReach — go-live checklist (v6 playbook)

**Launched 2026-05-22:** 216 Josh leads loaded into three **IN_PROGRESS** Wave1 campaigns (cluster routing). See `josh_campaign_ids.json`.

**Still manual for true v6 copy:** DRAFT campaign `441566` (`Josh-Pilot-20260522`, list `686853`) needs sequence pasted in UI from `heyreach_first_touch_v6_templates.md`.

## Done

- [x] Lead list **686808** — 216 unique profiles
- [x] Playbook node + v6 templates + cluster classifier in repo

## You (HeyReach UI)

1. [ ] Reconnect LinkedIn sender **Keegan Moody** (id `192406`)
2. [ ] Create **5 PAUSED** campaigns; paste first-DM copy from `heyreach_first_touch_v6_templates.md`:
   - `Josh-Pilot-ClusterA-Provider-20260522`
   - `Josh-Pilot-ClusterB-VBC-20260522`
   - `Josh-Pilot-ClusterC-CareMgmt-20260522`
   - `Josh-Pilot-ClusterD-Partnership-20260522`
   - `Josh-Pilot-ClusterE-Founder-20260522`
3. [ ] Sequence = connection request (short) → wait → **v6 first DM** (cluster template). Do not use deprecated `heyreach_lane_copy.md`.
4. [ ] Paste campaign IDs into `josh_campaign_ids.json` keys `A` through `E`
5. [ ] Review cluster dry-run: `python3 scripts/wire_josh_heyreach_campaigns.py`

## Load leads to campaigns (still paused)

```bash
python3 scripts/wire_josh_heyreach_campaigns.py --commit
```

## Go live (explicit approval)

1. [ ] Copy reviewed against hard rules (no em/en dash, no Hi, no folks, escape-hatch CTA present)
2. [ ] Set `"go_live_approved": true` in `josh_campaign_ids.json`
3. [ ] Start in UI **or** `python3 scripts/wire_josh_heyreach_campaigns.py --go-live`

**Volume:** ~25 connection requests/day per sender; 216 leads ≈ 9 days at one sender if all clusters run together.
