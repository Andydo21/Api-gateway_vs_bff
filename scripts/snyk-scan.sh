#!/bin/bash

# Snyk Scan Script for API Gateway vs BFF
# This script scans all microservices for dependency vulnerabilities.

echo "Starting Snyk Dependency Scan..."

# List of services to scan
SERVICES=("api-gateway" "bff/web-bff" "bff/admin-bff" "microservices/user-service" "microservices/product-service" "microservices/order-service" "microservices/payment-service" "microservices/inventory-service" "microservices/recommendation-service" "microservices/notification-service")

for SERVICE in "${SERVICES[@]}"; do
    echo "----------------------------------------------------"
    echo "Scanning service: $SERVICE"
    if [ -f "$SERVICE/requirements.txt" ]; then
        snyk test --file="$SERVICE/requirements.txt" --package-manager=pip
    else
        echo "No requirements.txt found in $SERVICE. Skipping."
    fi
done

echo "----------------------------------------------------"
echo "Snyk Scan Completed."
