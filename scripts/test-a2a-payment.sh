#!/bin/bash
# Test A2A + AP2 payment workflow

set -e

echo "🧪 Testing A2A + AP2 Payment Workflow"
echo "======================================"

# Check if A2A runtime exists
if [ ! -f .agentcore-a2a-arn ]; then
    echo "❌ A2A runtime not deployed. Run: ./scripts/deploy-a2a-complete.sh"
    exit 1
fi

A2A_ARN=$(cat .agentcore-a2a-arn)
echo "✅ A2A Runtime: $A2A_ARN"

# Check payment bucket
BUCKET_EXISTS=$(aws s3 ls s3://booking-agent-payments 2>/dev/null && echo "yes" || echo "no")
if [ "$BUCKET_EXISTS" = "yes" ]; then
    echo "✅ Payment bucket exists"
else
    echo "⚠️  Payment bucket not found (will be created on first payment)"
fi

echo ""
echo "📋 Test Scenarios:"
echo ""
echo "1. Book via MCP (Claude Desktop):"
echo "   'Book a table at La Bella Vita for Friday 8pm, 4 people'"
echo ""
echo "2. Agent will:"
echo "   - Check availability"
echo "   - Create booking"
echo "   - Request payment ($20 USDC for 4 people)"
echo "   - Return booking_id"
echo ""
echo "3. Approve payment:"
echo "   Use approve_payment tool with booking_id"
echo ""
echo "4. Verify payment:"
echo "   aws s3 ls s3://booking-agent-payments/payments/"
echo ""
echo "🔗 A2A Agent Card:"
echo "   https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/${A2A_ARN}/invocations/.well-known/agent-card.json"
