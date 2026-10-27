#!/bin/bash
# Continuous test load generator for Observability stack

TARGET_URL="${1:-http://localhost:5000}"
echo "Sending synthetic traffic to $TARGET_URL..."

while true; do
  curl -s "$TARGET_URL/" > /dev/null
  curl -s "$TARGET_URL/work" > /dev/null
  curl -s "$TARGET_URL/slow" > /dev/null
  curl -s "$TARGET_URL/error" > /dev/null
  sleep 0.3
done
