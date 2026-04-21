#!/usr/bin/env bash

set -euo pipefail

SERVICE_URL=${SERVICE_URL:-"http://localhost:5731"}

echo "🚀 Running smoke tests against: $SERVICE_URL"

# -------- 1. Health Check --------
echo "🔎 Checking /health..."
curl -fs "$SERVICE_URL/api/health"
echo "✅ Health OK"

# -------- 2. Stats Check --------
echo "🔎 Checking /stats..."
curl -fs "$SERVICE_URL/api/stats"
echo "✅ Stats OK"

# -------- 3. Start Scan --------
echo "🔎 Starting scan..."

SCAN_ID="smoke-$(date +%s)"

SCAN_RESPONSE=$(curl -s -X POST "$SERVICE_URL/api/scan/start" \
  -H "Content-Type: application/json" \
  -d "{
    \"config\": {
      \"scanId\": \"$SCAN_ID\",
      \"organizationId\": \"org-12345\",
      \"type\": [\"data\"],
      \"auth\": {
        \"accessToken\": \"${EMONEY_TOKEN:-dummy-token}\"
      },
      \"filters\": {
        \"properties\": [\"id\", \"name\", \"status\"],
        \"includeArchived\": false
      }
    }
  }")

echo "Response: $SCAN_RESPONSE"

# Extract scanId (fallback if API returns differently)
RETURNED_SCAN_ID=$(echo "$SCAN_RESPONSE" | jq -r '.scanId // empty')

if [ -z "$RETURNED_SCAN_ID" ]; then
  echo "❌ Failed to get scanId"
  exit 1
fi

echo "✅ Scan started: $RETURNED_SCAN_ID"

# -------- 4. Check Status with Retry --------
echo "🔎 Checking scan status..."

for i in {1..10}; do
  STATUS_RESPONSE=$(curl -s "$SERVICE_URL/scan/$RETURNED_SCAN_ID/status")

  echo "Attempt $i: $STATUS_RESPONSE"

  if echo "$STATUS_RESPONSE" | grep -qE "running|pending|completed"; then
    echo "✅ Scan status OK"
    exit 0
  fi

  echo "⏳ Waiting..."
  sleep 5
done

echo "❌ Smoke test failed: status endpoint not responding correctly"
exit 1