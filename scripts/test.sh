#!/usr/bin/env bash
set -e

echo "🧪 Testing WhatsApp Integration"
echo ""

# Get CDK outputs
cd cdk_infra
SNS_TOPIC=$(uv run cdk output WhatsAppStack.SNSTopicArn 2>/dev/null || echo "")
LAMBDA_NAME=$(uv run cdk output WhatsAppStack.OrchestratorName 2>/dev/null || echo "")
cd ..

if [ -z "$SNS_TOPIC" ] || [ -z "$LAMBDA_NAME" ]; then
    echo "❌ Stack not deployed. Run ./scripts/deploy.sh first"
    exit 1
fi

echo "📍 SNS Topic: ${SNS_TOPIC}"
echo "📍 Lambda: ${LAMBDA_NAME}"
echo ""

# Test messages
TESTS=(
    "Hello"
    "What is 5 + 5?"
    "What is Amazon Bedrock?"
)

for i in "${!TESTS[@]}"; do
    echo "Test $((i+1)): ${TESTS[$i]}"
    aws sns publish \
        --topic-arn "${SNS_TOPIC}" \
        --message "{\"from\": \"+1234567890\", \"text\": {\"body\": \"${TESTS[$i]}\"}}" \
        --query MessageId --output text
    echo "✅ Published"
    echo ""
    sleep 3
done

# Show logs
echo "📋 Recent logs:"
aws logs tail "/aws/lambda/${LAMBDA_NAME}" \
    --since 1m --format short \
    | grep -E "(WhatsApp from|AI reply)" || echo "No logs yet"

echo ""
echo "✅ Tests complete"
