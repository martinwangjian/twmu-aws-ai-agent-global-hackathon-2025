# WhatsApp Integration Testing Guide

## Testing Levels

### 1. Unit Tests (Lambda Handler)

Test Lambda orchestrator logic without AWS

### 2. Integration Tests (SNS → Lambda)

Test SNS to Lambda flow

### 3. E2E Tests (WhatsApp → Response)

Test full WhatsApp message flow

---

## 1. Unit Tests

### Test Lambda Handler Locally

```bash
# Create test event
cat > /tmp/test-sns-event.json << 'EOF'
{
  "Records": [{
    "Sns": {
      "Message": "{\"from\": \"+1234567890\", \"text\": {\"body\": \"Hello test\"}}"
    }
  }]
}
EOF

# Test locally (requires AWS credentials)
cd lambda
python3 << 'PYTHON'
import json
import os
os.environ["AGENTCORE_RUNTIME_ARN"] = "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/agentcore_mcp_agent-EXAMPLE"
os.environ["WHATSAPP_BUSINESS_ACCOUNT_ID"] = "waba-ea04858844fa4c68b1248a47be914ea9"

from whatsapp_orchestrator import handler

event = json.load(open("/tmp/test-sns-event.json"))
result = handler(event, type('obj', (object,), {'aws_request_id': 'test-123'}))
print(json.dumps(result, indent=2))
PYTHON
```

---

## 2. Integration Tests (SNS → Lambda)

### Test 1: Publish to SNS Topic

```bash
# Set environment
export $(grep -v '^#' .env | xargs)

# Publish test message
aws sns publish \
  --topic-arn "arn:aws:sns:us-east-1:123456789012:WhatsAppMessages" \
  --message '{
    "from": "+1234567890",
    "text": {"body": "What is AWS Lambda?"}
  }'
```

### Test 2: Check Lambda Logs

```bash
# Tail logs (real-time)
aws logs tail /aws/lambda/WhatsAppStack-WhatsAppOrchestrator64031DA7-tv8ahUJbQJJk \
  --follow

# Or check last 5 minutes
aws logs tail /aws/lambda/WhatsAppStack-WhatsAppOrchestrator64031DA7-tv8ahUJbQJJk \
  --since 5m --format short
```

**Expected Output**:

```
WhatsApp from +1234567890: What is AWS Lambda?
AI reply: AWS Lambda is a serverless compute service...
```

### Test 3: Verify AgentCore Invocation

```bash
# Check AgentCore logs
aws logs tail /aws/bedrock-agentcore/runtimes/agentcore_mcp_agent-EXAMPLE-DEFAULT \
  --since 5m --format short
```

---

## 3. E2E Tests (Manual WhatsApp)

### Prerequisites

1. WhatsApp Business channel configured in AWS Console
2. Phone number verified
3. SNS Topic ARN configured as event destination

### Test Scenarios

#### Scenario 1: Simple Question

**Send**: "Hello"
**Expected**: Greeting response from AI

#### Scenario 2: Math Question

**Send**: "What is 25 + 75?"
**Expected**: "25 + 75 = 100"

#### Scenario 3: AWS Knowledge

**Send**: "Explain Amazon Bedrock"
**Expected**: Detailed explanation of Bedrock

#### Scenario 4: Conversation Context

**Send**: "My name is John"
**Send**: "What is my name?"
**Expected**: "Your name is John" (tests session persistence)

---

## 4. Automated BDD Tests

### Create WhatsApp E2E Feature

```gherkin
# tests/features/whatsapp_e2e.feature
Feature: WhatsApp to AgentCore Integration
  As a WhatsApp user
  I want to send messages to the booking bot
  So that I can get AI-powered responses

  @e2e @whatsapp
  Scenario: Send message via SNS
    Given the WhatsApp stack is deployed
    When I publish a message to SNS Topic
    Then Lambda should process the message
    And AgentCore should be invoked
    And response should be logged

  @integration @whatsapp
  Scenario: Lambda handles WhatsApp message format
    Given a WhatsApp message event
    When Lambda orchestrator processes it
    Then it should extract phone number
    And it should extract message text
    And it should create valid session ID
```

### Run Tests

```bash
# Run WhatsApp integration tests
pytest tests/features/whatsapp_e2e.feature -v

# Run with markers
pytest tests/ -m whatsapp
```

---

## 5. Load Testing

### Test Multiple Messages

```bash
# Send 10 messages rapidly
for i in {1..10}; do
  aws sns publish \
    --topic-arn "arn:aws:sns:us-east-1:123456789012:WhatsAppMessages" \
    --message "{\"from\": \"+123456789$i\", \"text\": {\"body\": \"Test $i\"}}"
  echo "Sent message $i"
done

# Check Lambda concurrency
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name ConcurrentExecutions \
  --dimensions Name=FunctionName,Value=WhatsAppStack-WhatsAppOrchestrator64031DA7-tv8ahUJbQJJk \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Maximum
```

---

## 6. Error Scenarios

### Test 1: Invalid Message Format

```bash
aws sns publish \
  --topic-arn "arn:aws:sns:us-east-1:123456789012:WhatsAppMessages" \
  --message '{"invalid": "format"}'
```

**Expected**: Lambda handles gracefully, logs error

### Test 2: Empty Message

```bash
aws sns publish \
  --topic-arn "arn:aws:sns:us-east-1:123456789012:WhatsAppMessages" \
  --message '{"from": "+1234567890", "text": {"body": ""}}'
```

**Expected**: Lambda processes with default prompt

### Test 3: AgentCore Timeout

```bash
# Send very complex prompt
aws sns publish \
  --topic-arn "arn:aws:sns:us-east-1:123456789012:WhatsAppMessages" \
  --message '{"from": "+1234567890", "text": {"body": "Write a 10000 word essay"}}'
```

**Expected**: Lambda timeout or AgentCore handles within limits

---

## 7. Monitoring & Metrics

### CloudWatch Metrics

```bash
# Lambda invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=WhatsAppStack-WhatsAppOrchestrator64031DA7-tv8ahUJbQJJk \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Lambda errors
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=WhatsAppStack-WhatsAppOrchestrator64031DA7-tv8ahUJbQJJk \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Lambda duration
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=WhatsAppStack-WhatsAppOrchestrator64031DA7-tv8ahUJbQJJk \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

---

## 8. Quick Test Script

```bash
#!/bin/bash
# scripts/test-whatsapp.sh

set -e

echo "🧪 Testing WhatsApp Integration"

# Load environment
export $(grep -v '^#' .env | xargs)

# Test 1: Simple message
echo "Test 1: Simple message"
MESSAGE_ID=$(aws sns publish \
  --topic-arn "arn:aws:sns:us-east-1:123456789012:WhatsAppMessages" \
  --message '{"from": "+1234567890", "text": {"body": "Hello"}}' \
  --query MessageId --output text)
echo "✅ Published: $MESSAGE_ID"

# Wait for processing
sleep 5

# Check logs
echo "Checking logs..."
aws logs tail /aws/lambda/WhatsAppStack-WhatsAppOrchestrator64031DA7-tv8ahUJbQJJk \
  --since 1m --format short | grep -E "(WhatsApp from|AI reply)"

echo "✅ Test complete"
```

---

## Success Criteria

### Integration Test Passes When:

- ✅ SNS message published successfully
- ✅ Lambda invoked by SNS
- ✅ Message parsed correctly
- ✅ AgentCore invoked with valid session ID
- ✅ Response received from Bedrock
- ✅ No errors in CloudWatch logs
- ✅ Response time < 5 seconds

### E2E Test Passes When:

- ✅ WhatsApp message sent
- ✅ AWS End User Messaging receives it
- ✅ SNS Topic receives event
- ✅ Lambda processes message
- ✅ AgentCore generates response
- ✅ Response logged (or sent back to WhatsApp)

---

## Troubleshooting

### No logs appearing

**Check**:

```bash
# Verify Lambda subscription
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:123456789012:WhatsAppMessages

# Check Lambda permissions
aws lambda get-policy \
  --function-name WhatsAppStack-WhatsAppOrchestrator64031DA7-tv8ahUJbQJJk
```

### Lambda errors

**Check**:

```bash
# Get error details
aws logs filter-log-events \
  --log-group-name /aws/lambda/WhatsAppStack-WhatsAppOrchestrator64031DA7-tv8ahUJbQJJk \
  --filter-pattern "ERROR" \
  --start-time $(date -u -d '10 minutes ago' +%s)000
```

### AgentCore not responding

**Check**:

```bash
# Verify AgentCore status
aws bedrock-agentcore get-agent-runtime \
  --agent-runtime-arn arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/agentcore_mcp_agent-EXAMPLE
```

---

## Next Steps

After successful testing:

1. Implement reply functionality (send messages back to WhatsApp)
2. Add conversation state management
3. Integrate business-specific knowledge
4. Add booking logic with Google Calendar
5. Deploy to production
