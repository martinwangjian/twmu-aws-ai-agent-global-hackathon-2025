#!/bin/bash
# Reset sessions and memory for AgentCore

set -e

echo "🧹 Resetting sessions and memory..."

# Load environment
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

SESSION_BUCKET="agentcore-sessions-${AWS_ACCOUNT_ID:-<YOUR_AWS_ACCOUNT_ID>}"
MEMORY_ID=$(grep "AGENTCORE_MEMORY_ARN" .env 2>/dev/null | cut -d'=' -f2 | cut -d':' -f6)

# Clear all sessions
echo "📂 Clearing S3 sessions..."
aws s3 rm s3://${SESSION_BUCKET}/ --recursive --region us-east-1 --quiet || echo "⚠️  No sessions to clear"
echo "✅ Sessions cleared"

# Clear memory (if memory ID exists)
if [ -n "$MEMORY_ID" ]; then
    echo "🧠 Clearing AgentCore memory..."
    aws bedrock-agentcore delete-memory-events \
        --memory-id "$MEMORY_ID" \
        --region us-east-1 2>/dev/null && echo "✅ Memory cleared" || echo "⚠️  Memory already empty or not found"
else
    echo "⚠️  No memory ID found in .env"
fi

echo ""
echo "✅ Reset complete!"
