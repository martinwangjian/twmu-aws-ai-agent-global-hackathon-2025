#!/bin/bash
# Copyright (C) 2025 Teamwork Mauritius
# AGPL-3.0 License

set -e

echo "🧪 Testing Phase 1: Response Cleaning"
echo "======================================"
echo ""

# Source environment
source .env

# Test 1: AgentCore direct
echo "Test 1: AgentCore Direct Invocation"
echo "------------------------------------"
uv run agentcore invoke '{"prompt": "Hello, I want to book a table", "actor_id": "test-user"}' | grep -o '"result": "[^"]*"' | sed 's/"result": "//;s/"$//'
echo ""

# Test 2: Lambda via alias
echo "Test 2: Lambda Invocation (via alias)"
echo "--------------------------------------"
FUNCTION_NAME=$(aws cloudformation describe-stacks --stack-name WhatsAppStack --query 'Stacks[0].Outputs[?OutputKey==`OrchestratorName`].OutputValue' --output text)

aws lambda invoke \
  --function-name "${FUNCTION_NAME}:live" \
  --cli-binary-format raw-in-base64-out \
  --payload '{"body": "{\"messages\": [{\"from\": \"+23012345678\", \"text\": {\"body\": \"Hello, I want to book a table\"}}]}"}' \
  /tmp/lambda-response.json > /dev/null

echo "Response:"
cat /tmp/lambda-response.json | jq -r '.body' | jq -r '.message'
echo ""

# Verification
echo "✅ Verification Checklist:"
echo "  [ ] No <think> or <thinking> tags visible"
echo "  [ ] Responses are natural and conversational"
echo "  [ ] Both AgentCore and Lambda show same behavior"
echo ""
echo "If all checks pass, Phase 1 is complete! ✅"
echo "Ready to proceed to Phase 2: Availability Checking"
