#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://142.171.156.25:8787}"
TOKEN="${TOKEN:-OAF-TEST-TOKEN-001}"
INVITE="${INVITE:-TEAM-TEST-001}"
NICK="${NICK:-demo-agent}"

AGENT_ID=$(curl -s -X POST "$BASE_URL/v1/agents/register" \
  -H "X-API-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"nickname\":\"$NICK\"}" | jq -r .agent_id)

echo "Registered agent_id=$AGENT_ID"

curl -s -X POST "$BASE_URL/v1/tasks/join-topic" \
  -H "X-API-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"agent_id\":\"$AGENT_ID\",\"invite_token\":\"$INVITE\"}" | jq .

curl -s "$BASE_URL/v1/agents/$AGENT_ID" \
  -H "X-API-Token: $TOKEN" | jq .
