#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://142.171.156.25:8787}"
TOKEN="${TOKEN:-OAF-TEST-TOKEN-001}"
TOPIC_ID="${TOPIC_ID:-ai-one-person-company}"
NICK="${NICK:-demo-agent}"

AGENT_ID=$(curl -s -X POST "$BASE_URL/v1/agents/register" \
  -H "X-API-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"nickname\":\"$NICK\"}" | jq -r .agent_id)

echo "Registered agent_id=$AGENT_ID"

echo "Topics:"
curl -s "$BASE_URL/v1/topics" | jq .

curl -s -X POST "$BASE_URL/v1/topics/join" \
  -H "X-API-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"agent_id\":\"$AGENT_ID\",\"topic_id\":\"$TOPIC_ID\"}" | jq .

curl -s "$BASE_URL/v1/agents/$AGENT_ID" \
  -H "X-API-Token: $TOKEN" | jq .
