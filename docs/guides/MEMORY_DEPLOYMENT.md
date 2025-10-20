# Memory Feature Deployment Guide

## Prerequisites

- AgentCore runtime already deployed
- AWS credentials configured
- CDK environment set up

## Step 1: Configure AgentCore Memory (Optional)

AgentCore memory is **automatically enabled** when you configure the agent. The memory ARN is created during AgentCore deployment.

To check if memory is configured:

```bash
# Check .bedrock_agentcore.yaml for memory section
cat .bedrock_agentcore.yaml | grep -A 3 "memory"
```

If memory ARN exists, note it down. If not, AgentCore will use session memory only (which is sufficient for most use cases).

## Step 2: Set Environment Variable (Optional)

If you have a memory ARN and want to use persistent memory:

```bash
export AGENTCORE_MEMORY_ARN="arn:aws:bedrock-agentcore:us-east-1:123456789012:memory/booking-agent-mem-EXAMPLE"
```

**Note**: If you don't set this, the agent will still work with session memory (conversation continuity within the same day).

## Step 3: Deploy Lambda Update

```bash
cd cdk_infra
uv run cdk deploy WhatsAppStack
```

This will:

- Update Lambda with memory support code
- Add AGENTCORE_MEMORY_ARN environment variable (if set)
- Enable daily session ID generation

## Step 4: Test Memory

### Test 1: Session Memory (Same Day)

```bash
# Send first message
aws sns publish \
  --topic-arn "arn:aws:sns:us-east-1:123456789012:WhatsAppMessages" \
  --message '{
    "from": "+1234567890",
    "body": "My name is John and I prefer morning appointments"
  }'

# Send second message (same day)
aws sns publish \
  --topic-arn "arn:aws:sns:us-east-1:123456789012:WhatsAppMessages" \
  --message '{
    "from": "+1234567890",
    "body": "What is my name and preference?"
  }'
```

**Expected**: Agent remembers "John" and "morning appointments"

### Test 2: Using Test Script

```bash
# Set AgentCore ARN
export AGENTCORE_RUNTIME_ARN=$(cat .agentcore-runtime-arn)

# Optional: Set memory ARN
export AGENTCORE_MEMORY_ARN="your-memory-arn"

# Run test
uv run python scripts/test_memory.py
```

**Expected Output**:

```
============================================================
Testing AgentCore Memory
============================================================
Session ID: test:202510080900

=== Test 1: Store Information ===
User: My name is John and I prefer morning appointments at 10am
Agent: [Response acknowledging the information]

=== Test 2: Recall Information ===
User: What's my name and what time do I prefer?
Agent: [Response mentioning John and 10am/morning]

=== Verification ===
✅ Passed: Name remembered
✅ Passed: Preference remembered

============================================================
✅ Memory test PASSED!
============================================================
```

## Verification

### Check Lambda Logs

```bash
aws logs tail /aws/lambda/WhatsAppStack-WhatsAppOrchestrator --follow
```

Look for:

```
Session ID: whatsapp:+1234567890:20251008
Using memory ARN: arn:aws:bedrock-agentcore:...
```

### Check Session Continuity

1. Send a message in the morning
2. Send another message in the afternoon (same day)
3. Verify agent remembers context from morning

## How It Works

### Session ID Format

```
whatsapp:{phone_number}:{date}
```

Example: `whatsapp:+1234567890:20251008`

- **Same day**: Same session ID → conversation continuity
- **Next day**: New session ID → fresh start

### Memory Behavior

**Without Memory ARN** (Session Memory Only):

- Remembers within same day
- Resets at midnight UTC
- No cost

**With Memory ARN** (Persistent Memory):

- Remembers across days
- Stores user preferences
- Included in AgentCore cost

## Troubleshooting

### Memory Not Working

1. **Check session ID**:

   ```bash
   aws logs filter-pattern "Session ID" \
     --log-group-name /aws/lambda/WhatsAppStack-WhatsAppOrchestrator
   ```

2. **Verify memory ARN**:

   ```bash
   aws lambda get-function-configuration \
     --function-name WhatsAppStack-WhatsAppOrchestrator \
     --query 'Environment.Variables.AGENTCORE_MEMORY_ARN'
   ```

3. **Check AgentCore logs**:
   ```bash
   # Memory errors will appear in Lambda logs
   aws logs tail /aws/lambda/WhatsAppStack-WhatsAppOrchestrator --since 1h
   ```

### Session Not Persisting

- **Issue**: New session ID every message
- **Cause**: Phone number format inconsistent
- **Fix**: Ensure phone number includes country code (e.g., +1234567890)

### Memory ARN Not Found

- **Issue**: `AGENTCORE_MEMORY_ARN` not set
- **Solution**: This is optional. Agent works without it using session memory.

## Rollback

If you need to rollback:

```bash
git revert HEAD
cd cdk_infra
uv run cdk deploy WhatsAppStack
```

## Cost

- **Session Memory**: $0 (included)
- **Persistent Memory**: $0 (included in AgentCore)
- **No additional charges**

## Next Steps

- Monitor memory usage in CloudWatch
- Adjust session TTL if needed
- Consider adding DynamoDB for structured data (Phase 2)

---

**Status**: Deployed
**Version**: 1.0
**Last Updated**: 2025-10-08
