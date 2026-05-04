#!/usr/bin/env bash
# Read-oriented InboxKit API sweep for local testing / weekly reporting.
# Mailboxes: use POST /v1/api/mailboxes/list (+ X-Workspace-Id when required); GET /v1/mailboxes is not valid.
# Usage: export INBOXKIT_API_KEY='...'; bash scripts/inboxkit_api_smoke.sh
# Writes full payloads to OUT (default under /tmp) and prints a compact status table.

set -euo pipefail

BASE_URL="${INBOXKIT_BASE_URL:-https://api.inboxkit.com}"
: "${INBOXKIT_API_KEY:?ERROR: Export INBOXKIT_API_KEY before running}"

OUT="${INBOXKIT_SMOKE_OUT:-/tmp/inboxkit_smoke_$(date +%Y%m%d_%H%M%S)}"
mkdir -p "$OUT"

hdr_auth=(-H "Authorization: Bearer ${INBOXKIT_API_KEY}")
hdr_json=(-H "Content-Type: application/json")

# Usage: ik_curl NAME METHOD PATH [-- curl-extra ...]
ik_curl() {
  local name="$1" method="$2" path="$3"
  shift 3
  local outfile="${OUT}/${name}.txt"
  local code hpayload
  set +e
  code="$(curl -sS -o "$outfile" -w "%{http_code}" -X "$method" \
    "${hdr_auth[@]}" "${hdr_json[@]}" "$@" "${BASE_URL}${path}")"
  hpayload="$?"
  set -e
  if [[ "$hpayload" -ne 0 ]]; then
    echo "$name	FAIL(transport)	code=-"
    return 0
  fi
  echo "$name	${method}	${path}	${code}" >>"${OUT}/_index.tsv"
  echo "$name	http=${code}"
}

echo "Recording under: $OUT"

# --- Team-wide (no workspace header) ---
ik_curl "01_account" GET "/v1/api/account"
ik_curl "02_workspaces_list" GET "/v1/api/workspaces/list"
ik_curl "03_billing_pricing_plans" GET "/v1/api/billing/pricing-plans"
ik_curl "04_billing_subscription" GET "/v1/api/billing/subscription"
ik_curl "05_billing_wallet" GET "/v1/api/billing/wallet"
ik_curl "06_billing_wallet_logs" GET "/v1/api/billing/wallet/logs"
ik_curl "07_billing_manage_portal_link" GET "/v1/api/billing/manage"

# Workspace UID: try standard .uid; fall back to .workspaces[0].uid variants
WL="${OUT}/02_workspaces_list.txt"
if [[ ! -s "$WL" ]]; then
  echo "WARN: workspaces list missing; skipping workspace-scoped calls"
  WS=""
else
  WS="$(jq -r '.workspaces[0].uid // .workspaces[0].workspace_uid // .data[0].uid // empty' "$WL" 2>/dev/null || true)"
  if [[ -z "$WS" || "$WS" == "null" ]]; then
    WS="$(jq -r '.[0].uid // empty' "$WL" 2>/dev/null || true)"
  fi
fi

if [[ -n "${WS:-}" ]]; then
  echo "Using X-Workspace-Id (first workspace): ${WS}"
  ik_curl "08_consent_requests" GET "/v1/api/mailboxes/consent-requests?limit=20&offset=0" \
    -H "X-Workspace-Id: ${WS}"
  ik_curl "10_workspace_details" GET "/v1/api/workspaces/details?uid=${WS}"

  ik_curl "11_domains_list" POST "/v1/api/domains/list" \
    -H "X-Workspace-Id: ${WS}" \
    --data-binary '{"page":1,"limit":50}'

  ik_curl "12_domains_assignable" GET "/v1/api/domains/assignable?page=1&limit=50" \
    -H "X-Workspace-Id: ${WS}"

  ik_curl "13_mailboxes_list" POST "/v1/api/mailboxes/list" \
    -H "X-Workspace-Id: ${WS}" \
    --data-binary '{"page":1,"limit":50}'

  ik_curl "14_tags_list" GET "/v1/api/tags" \
    -H "X-Workspace-Id: ${WS}"

  ik_curl "15_cloudflare_domains" GET "/v1/api/cloudflare-domains/list?page=1&limit=50" \
    -H "X-Workspace-Id: ${WS}"

  ik_curl "16_sequencer_platforms" GET "/v1/api/sequencers/platforms" \
    -H "X-Workspace-Id: ${WS}"

  ik_curl "17_sequencers_list" POST "/v1/api/sequencers/list" \
    -H "X-Workspace-Id: ${WS}" \
    --data-binary '{"limit":50,"offset":0}'

  ik_curl "18_mailboxes_client_id_requests" GET "/v1/api/mailboxes/client-id-requests?page=1&limit=20" \
    -H "X-Workspace-Id: ${WS}"

  ik_curl "19_warmup_list" POST "/v1/api/warmup/list" \
    -H "X-Workspace-Id: ${WS}" \
    --data-binary '{"page":1,"limit":50}'

  ik_curl "20_warmup_pricing" GET "/v1/api/warmup/pricing" \
    -H "X-Workspace-Id: ${WS}"

  ik_curl "21_warmup_stats" GET "/v1/api/warmup/stats" \
    -H "X-Workspace-Id: ${WS}"

  ik_curl "22_inbox_placement_tests" GET "/v1/api/inbox-placement/tests" \
    -H "X-Workspace-Id: ${WS}"

  ik_curl "23_inbox_placement_scheduled" GET "/v1/api/inbox-placement/scheduled" \
    -H "X-Workspace-Id: ${WS}"

  ik_curl "24_infra_guard_pricing" GET "/v1/api/infra-guard/pricing" \
    -H "X-Workspace-Id: ${WS}"

  ik_curl "25_infra_guard_stats" GET "/v1/api/infra-guard/stats" \
    -H "X-Workspace-Id: ${WS}"

  DU="$(jq -r '.domains[0].uid // empty' "${OUT}/11_domains_list.txt" 2>/dev/null || true)"
  if [[ -n "${DU:-}" && "$DU" != "null" ]]; then
    ik_curl "26_infra_guard_bounce_metrics" GET "/v1/api/infra-guard/bounce-metrics?uid=${DU}&period_days=7" \
      -H "X-Workspace-Id: ${WS}"
  else
    echo "26_infra_guard_bounce_metrics	SKIPPED (no domain uid)"
  fi

  ik_curl "27_email_insights_overview" GET "/v1/api/email-insights/workspace/overview" \
    -H "X-Workspace-Id: ${WS}"

  ik_curl "28_email_insights_mailboxes_health" GET "/v1/api/email-insights/workspace/mailboxes-health" \
    -H "X-Workspace-Id: ${WS}"

  ik_curl "29_email_insights_high_bounce" GET "/v1/api/email-insights/workspace/high-bounce-mailboxes" \
    -H "X-Workspace-Id: ${WS}"

  ik_curl "30_email_insights_workspace_activity" GET "/v1/api/email-insights/workspace/activity" \
    -H "X-Workspace-Id: ${WS}"

  MU="$(jq -r '.mailboxes[0].uid // .data[0].uid // empty' "${OUT}/13_mailboxes_list.txt" 2>/dev/null || true)"
  if [[ -n "${MU:-}" && "$MU" != "null" ]]; then
    ik_curl "31_mailbox_detail" GET "/v1/api/mailboxes/details?uid=${MU}" \
      -H "X-Workspace-Id: ${WS}"
    ik_curl "32_email_insights_mailbox_stats" GET "/v1/api/email-insights/mailbox/${MU}/stats" \
      -H "X-Workspace-Id: ${WS}"
    ik_curl "33_email_insights_mailbox_health" GET "/v1/api/email-insights/mailbox/${MU}/health" \
      -H "X-Workspace-Id: ${WS}"
  else
    echo "31_mailbox_detail	SKIPPED (no mailbox uid)"
  fi
else
  echo "WARN: Could not resolve workspace UID from /v1/api/workspaces/list"
fi

# Bundle one JSON document for archiving (responses + http bodies as text)
SUMMARY_JSON="${OUT}/_bundle_summary.json"
{
  echo '{"base_url":"'"${BASE_URL}"'","artifacts":['
  first=1
  for f in "$OUT"/*.txt; do
    [[ -f "$f" ]] || continue
    base="$(basename "$f" .txt)"
    [[ "$base" =~ ^_ ]] && continue
    code=""
    [[ -f "${OUT}/_index.tsv" ]] && code="$(grep -E "^${base}	" "${OUT}/_index.tsv" 2>/dev/null | awk -F'	' '{print $4}' | head -1 || true)"
    body="$(cat "$f" | python3 -c 'import sys,json; sys.stdout.write(json.dumps(sys.stdin.read()))')"
    [[ $first -eq 1 ]] && first=0 || echo ','
    echo -n "{\"name\":\"${base}\",\"http\":${code:-0},\"response\":${body}}"
  done
  echo ']}'
} >"${SUMMARY_JSON}.tmp"
mv "${SUMMARY_JSON}.tmp" "$SUMMARY_JSON"

echo ""
echo "--- Done. Open: ${OUT}"
echo "Summary bundle: ${SUMMARY_JSON}"
echo "--- Non-JSON or huge files: still in *.txt next to bundle"
