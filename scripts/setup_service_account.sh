#!/bin/bash
# Setup Google Calendar with Service Account

set -e

echo "=========================================="
echo "Google Calendar Service Account Setup"
echo "=========================================="

# Check if service account key exists
if [ ! -f "service-account-key.json" ]; then
    echo ""
    echo "❌ service-account-key.json not found!"
    echo ""
    echo "Please create a Service Account:"
    echo "1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts"
    echo "2. Create service account: 'restaurant-booking-agent'"
    echo "3. Create JSON key"
    echo "4. Save as 'service-account-key.json' in project root"
    echo ""
    echo "Then share your calendar with the service account email."
    exit 1
fi

echo "✓ Found service-account-key.json"

# Extract service account email
SERVICE_ACCOUNT_EMAIL=$(cat service-account-key.json | python3 -c "import sys, json; print(json.load(sys.stdin)['client_email'])")
echo "✓ Service Account: $SERVICE_ACCOUNT_EMAIL"

echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "1. Share your Google Calendar with:"
echo "   $SERVICE_ACCOUNT_EMAIL"
echo "   Permission: 'Make changes to events'"
echo ""
echo "2. Deploy Lambda function:"
echo "   cd cdk_infra"
echo "   uv run cdk deploy CalendarServiceStack"
echo ""
echo "3. Update Gateway to use Lambda target:"
echo "   uv run python scripts/update_gateway_to_lambda.py"
echo ""
echo "4. Test booking:"
echo "   uv run python scripts/test_gateway_booking.py"
echo ""
