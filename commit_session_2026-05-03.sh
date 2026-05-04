#!/usr/bin/env bash
# One-shot commit script for the 2026-05-03 session.
# Run from your local Terminal (not the agent sandbox):
#
#   cd ~/KIVIRA.HEALTH
#   bash commit_session_2026-05-03.sh
#
# Sandbox couldn't remove .git/index.lock, so this script handles it locally.

set -euo pipefail
cd "$(dirname "$0")"

echo "=== Clearing stale git index lock if present ==="
rm -f .git/index.lock

echo "=== Staging session files ==="
git add \
  scripts/build_list_1a.py \
  scripts/build_list_2b_2c.py \
  scripts/build_randomized_test_batch.py \
  scripts/extract_from_search_snippets.py \
  scripts/generate_spider_queries.py \
  scripts/heyreach_create_and_load_test.py \
  scripts/heyreach_load.py \
  scripts/spider_query_runner.py \
  tests/test_build_list_1a.py \
  tests/test_build_list_2b_2c.py \
  fixtures/canonical_linkedin_queries.md \
  fixtures/wave1_runs/20260503T165558Z \
  fixtures/wave1_runs/20260503T170232Z \
  fixtures/wave1_runs/20260503T170302Z \
  fixtures/wave1_runs/20260503T170340Z \
  fixtures/wave1_runs/20260503T170409Z

echo "=== Staged ==="
git diff --cached --stat
echo ""

echo "=== Committing ==="
git commit -m "feat(session 2026-05-03): cross-subtier baseline launch + canonical 9x5 adoption (LEC-45)

- 27 connection requests now sending in HeyReach (1A_OO + 1A_CC)
- 270-lead cross-subtier baseline test queued (list 647057, awaiting UI campaign)
- Canonical 9-subtier x 5-role taxonomy adopted from Miro source of truth

New scripts:
- build_list_2b_2c.py        MSSP persona pivot (490+509 named ACO contacts) + 9 tests
- extract_from_search_snippets.py  bypasses Parallel.ai cost; classifies persona+subtier
                                   from Spider snippets via existing tag_persona_keyword;
                                   1A account list wired as back-tag verifier
- heyreach_load.py           HeyReach API loader (POST /campaign/AddLeadsToCampaignV2)
- heyreach_create_and_load_test.py  list create + lead load (270-lead baseline)
- generate_spider_queries.py 37 Boolean queries from canonical 9x5 matrix
- build_randomized_test_batch.py    N-per-subtier sampler with shuffle

Modified scripts:
- build_list_1a.py           6-code taxonomy + NPPES org-size proxy + hospital/IDN/govt
                             noise filter; 1A: 52K -> 1,139 accounts (LEC-41 closed)
- spider_query_runner.py     alpha query IDs (Q1B-OO format) + --queries-file flag +
                             --search-limit flag (10 -> 30)

New fixtures:
- canonical_linkedin_queries.md  37 generated Boolean queries
- wave1_runs/20260503T*          5 Spider run directories (34 cells executed)

Tests: 27 passing (18 build_list_1a + 9 build_list_2b_2c)

Master CSV: 2,860 persona-tagged leads (was 20)

Linear: LEC-45 (this session retro), LEC-41 closed, LEC-43 + LEC-44 commented.
Memory: 4 feedback/project memories saved (Linear hygiene, broad-Boolean,
        canonical 9x5, Linear-as-proof-of-work)."

echo ""
echo "=== Done. Latest commit: ==="
git log --oneline -1
