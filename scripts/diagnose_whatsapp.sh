#!/bin/bash
# WhatsApp Integration Diagnostic Script

set -e

REGION="us-east-1"
PROFILE="twmu-sandbox"

echo "========================================="
echo "WhatsApp Integration Diagnostics"
echo "========================================="
echo ""

# 1. Check Lambda function
echo "1. Lambda Function Status:"
LAMBDA_NAME=$(aws lambda list-functions \
  --region $REGION \
  --profile $PROFILE \
  --query 'Functions[?contains(FunctionName, `WhatsAppOrchestrator`)].FunctionName' \
  --output text | head -1)

if [ -z "$LAMBDA_NAME" ]; then
  echo "❌ Lambda function not found"
  exit 1
else
  echo "✅ Lambda: $LAMBDA_NAME"
fi

# 2. Check SNS Topic
echo ""
echo "2. SNS Topic:"
SNS_ARN=$(aws cloudformation describe-stacks \
  --stack-name WhatsAppStack \
  --region $REGION \
  --profile $PROFILE \
  --query 'Stacks[0].Outputs[?OutputKey==`SNSTopicArn`].OutputValue' \
  --output text 2>/dev/null)

if [ -z "$SNS_ARN" ]; then
  echo "❌ SNS topic not found"
else
  echo "✅ SNS: $SNS_ARN"
fi

# 3. Check SNS Subscription
echo ""
echo "3. SNS → Lambda Subscription:"
SUB_COUNT=$(aws sns list-subscriptions-by-topic \
  --topic-arn "$SNS_ARN" \
  --region $REGION \
  --profile $PROFILE \
  --query 'length(Subscriptions)' \
  --output text 2>/dev/null)

if [ "$SUB_COUNT" -gt 0 ]; then
  echo "✅ Subscriptions: $SUB_COUNT"
else
  echo "❌ No subscriptions found"
fi

# 4. Check WhatsApp Account
echo ""
echo "4. WhatsApp Business Account:"
WABA_STATUS=$(aws socialmessaging list-linked-whatsapp-business-accounts \
  --region $REGION \
  --profile $PROFILE \
  --query 'linkedAccounts[0].registrationStatus' \
  --output text 2>/dev/null)

if [ "$WABA_STATUS" = "COMPLETE" ]; then
  echo "✅ Status: $WABA_STATUS"

  WABA_NAME=$(aws socialmessaging list-linked-whatsapp-business-accounts \
    --region $REGION \
    --profile $PROFILE \
    --query 'linkedAccounts[0].wabaName' \
    --output text)
  echo "   Name: $WABA_NAME"
else
  echo "❌ Status: $WABA_STATUS"
fi

# 5. Check Event Destination
echo ""
echo "5. WhatsApp → SNS Connection:"
EVENT_DEST=$(aws socialmessaging list-linked-whatsapp-business-accounts \
  --region $REGION \
  --profile $PROFILE \
  --query 'linkedAccounts[0].eventDestinations[0].eventDestinationArn' \
  --output text 2>/dev/null)

if [ "$EVENT_DEST" = "$SNS_ARN" ]; then
  echo "✅ Connected to SNS"
else
  echo "❌ Not connected to SNS"
  echo "   Expected: $SNS_ARN"
  echo "   Actual: $EVENT_DEST"
fi

# 6. Check Lambda Environment Variables
echo ""
echo "6. Lambda Configuration:"
RUNTIME_ARN=$(aws lambda get-function-configuration \
  --function-name "$LAMBDA_NAME" \
  --region $REGION \
  --profile $PROFILE \
  --query 'Environment.Variables.AGENTCORE_RUNTIME_ARN' \
  --output text 2>/dev/null)

if [ "$RUNTIME_ARN" != "None" ] && [ -n "$RUNTIME_ARN" ]; then
  echo "✅ AgentCore ARN configured"
else
  echo "❌ AgentCore ARN missing"
fi

# 7. Check Recent Logs
echo ""
echo "7. Recent Lambda Invocations:"
LOG_GROUP="/aws/lambda/$LAMBDA_NAME"
RECENT_LOGS=$(aws logs filter-log-events \
  --log-group-name "$LOG_GROUP" \
  --start-time $(($(date +%s) - 3600))000 \
  --region $REGION \
  --profile $PROFILE \
  --query 'events[0:3].[timestamp,message]' \
  --output text 2>/dev/null)

if [ -n "$RECENT_LOGS" ]; then
  echo "✅ Recent activity found"
  echo "$RECENT_LOGS" | head -5
else
  echo "⚠️  No recent logs (last hour)"
fi

# 8. Test SNS Publishing
echo ""
echo "8. Test SNS Message:"
echo "   Run this to test:"
echo "   aws sns publish --topic-arn \"$SNS_ARN\" --message '{\"from\":\"+1234567890\",\"body\":\"test\"}' --region $REGION --profile $PROFILE"

echo ""
echo "========================================="
echo "Diagnostic Complete"
echo "========================================="
