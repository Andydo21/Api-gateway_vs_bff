#!/bin/bash

# OWASP ZAP Baseline Scan Script
# This script runs a ZAP baseline scan against the API Gateway.

APP_URL=${1:-"http://localhost:8000"}
REPORT_DIR="reports"

echo "Starting OWASP ZAP Baseline Scan against $APP_URL..."

mkdir -p $REPORT_DIR

# Use Docker to run the ZAP baseline scan
# -t: target URL
# -r: report name
docker run --rm -v "$(pwd)/$REPORT_DIR:/zap/wrk/:rw" -t owasp/zap2docker-stable zap-baseline.py \
    -t "$APP_URL" \
    -r zap_report.html

echo "ZAP Scan Completed. Report available at $REPORT_DIR/zap_report.html"
