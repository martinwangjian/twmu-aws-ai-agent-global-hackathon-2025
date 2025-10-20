#!/bin/bash
# Complete deployment: WhatsApp + A2A + AP2

set -e

echo "🚀 Complete Deployment"
echo "======================"

# Load environment
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

export AWS_DEFAULT_REGION=us-east-1

# Step 1: Deploy CDK infrastructure
echo ""
echo "📦 Step 1/5: Deploy CDK Stacks..."
cd cdk_infra
uv run cdk deploy PaymentBucketStack CognitoStack ConfigStack --require-approval never
cd ..

# Step 2: Configure and deploy WhatsApp AgentCore
echo ""
echo "🤖 Step 2/5: Deploy WhatsApp AgentCore Runtime..."
uv run agentcore configure \
    --entrypoint src/agents/agentcore_mcp_agent.py \
    --requirements-file src/agents/requirements.txt \
    --region us-east-1 \
    --non-interactive

uv run agentcore launch --auto-update-on-conflict

# Reset sessions and memory
echo "🧹 Resetting sessions and memory..."
SESSION_BUCKET="agentcore-sessions-${AWS_ACCOUNT_ID}"
MEMORY_ID=$(grep "AGENTCORE_MEMORY_ARN" .env 2>/dev/null | cut -d'=' -f2 | cut -d':' -f6)

aws s3 rm s3://${SESSION_BUCKET}/ --recursive --region us-east-1 --quiet 2>/dev/null || echo "  ⚠️  No sessions to clear"

if [ -n "$MEMORY_ID" ]; then
    aws bedrock-agentcore delete-memory-events \
        --memory-id "$MEMORY_ID" \
        --region us-east-1 2>/dev/null || echo "  ⚠️  Memory already empty"
fi
echo "✅ Sessions and memory reset"

# Step 3: Deploy A2A AgentCore Runtime
echo ""
echo "🤖 Step 3/5: Deploy A2A AgentCore Runtime..."
uv run agentcore configure \
    --entrypoint src/agents/agentcore_a2a_server.py \
    --requirements-file src/agents/requirements-a2a.txt \
    --region us-east-1 \
    --protocol A2A \
    --authorizer-config '{"customJWTAuthorizer":{"discoveryUrl":"https://cognito-idp.us-east-1.amazonaws.com/us-east-1_rUMgDERTc/.well-known/openid-configuration","allowedAudience":["qli2ric7jaush0pjstogu4vua"]}}' \
    --non-interactive

uv run agentcore launch --auto-update-on-conflict

A2A_ARN=$(cat .agentcore-a2a-arn 2>/dev/null || echo "N/A")
echo "✅ A2A Runtime ARN: $A2A_ARN"

# Step 4: Deploy remaining CDK stacks
echo ""
echo "📦 Step 4/5: Deploy WhatsApp and Calendar Stacks..."
cd cdk_infra
uv run cdk deploy WhatsAppStack CalendarServiceStack --require-approval never
cd ..

# Deploy Knowledge Base via boto3 (S3_VECTORS not supported in CDK yet)
echo ""
echo "📚 Deploying Knowledge Base (boto3)..."
uv run python scripts/deploy_kb_boto3.py

# Step 5: Get Cognito token for A2A
echo ""
echo "🎫 Step 5/5: Get Cognito Bearer Token..."
./scripts/get_cognito_token.sh

# Update Claude Desktop config
./scripts/update-claude-config.sh

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📋 Deployed Components:"
echo "  - WhatsApp AgentCore Runtime (with memory)"
echo "  - A2A AgentCore Runtime (with OAuth)"
echo "  - Payment Bucket (S3)"
echo "  - Cognito User Pool (OAuth)"
echo "  - WhatsApp Lambda Orchestrator"
echo "  - Calendar Service Lambda"
echo "  - Knowledge Base"
echo ""
echo "📋 Next Steps:"
echo "  WhatsApp: Test via WhatsApp Business"
echo "  A2A: Restart Claude Desktop and test booking"
echo ""
echo "🔗 A2A Runtime: $A2A_ARN"
echo "🔗 Payment Bucket: booking-agent-payments"
