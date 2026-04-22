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
