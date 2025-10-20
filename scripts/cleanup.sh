#!/usr/bin/env bash
set -e

REGION="${AWS_REGION:-us-east-1}"

echo "🧹 Cleanup Resources"
echo ""
echo "This will delete:"
echo "  • CDK stacks (WhatsAppStack, BookingAgentStack)"
echo "  • AgentCore runtime"
echo "  • All associated AWS resources"
echo ""
read -p "Are you sure? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^yes$ ]]; then
    echo "❌ Cancelled"
    exit 0
fi

# 1. Delete CDK stacks
echo "📦 Deleting CDK stacks..."
cd cdk_infra
uv run cdk destroy --all --force || echo "⚠️  CDK stacks already deleted"
cd ..

# 2. Delete AgentCore
echo "📦 Deleting AgentCore..."
if [ -f .agentcore-runtime-arn ]; then
    RUNTIME_ARN=$(cat .agentcore-runtime-arn)
    aws bedrock-agentcore delete-agent-runtime \
        --agent-runtime-arn "${RUNTIME_ARN}" \
        --region ${REGION} || echo "⚠️  Runtime already deleted"
    rm -f .agentcore-runtime-arn
    echo "✅ Deleted: ${RUNTIME_ARN}"
else
    echo "⚠️  No AgentCore runtime found"
fi

echo ""
echo "✅ Cleanup complete"
