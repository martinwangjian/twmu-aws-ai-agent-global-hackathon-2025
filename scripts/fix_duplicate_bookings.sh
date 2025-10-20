#!/bin/bash
# Fix duplicate bookings by updating Gateway and redeploying agent

set -e

echo "=================================================="
echo "🔧 Fixing Duplicate Bookings"
echo "=================================================="
echo ""

# Check we're in the right directory
if [ ! -f "gateway_config.json" ]; then
    echo "❌ Error: gateway_config.json not found"
    echo "Please run this script from the project root"
    exit 1
fi

echo "Step 1: Export CDK outputs"
echo "--------------------------------------------"
./scripts/export_cdk_outputs.sh
echo ""

echo "Step 2: Redeploy AgentCore with updated system prompt"
echo "----------------------------------------------------"
uv run agentcore launch
echo ""

echo "=================================================="
echo "✅ Fix deployed successfully!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Test with A2A booking request"
echo "2. Verify agent calls checkAvailability first"
echo "3. Confirm only 1 event created in calendar"
echo ""
echo "Test command:"
echo "  # Use Claude Desktop A2A to make a booking"
echo "  # Check AgentCore logs for tool calls"
echo ""
