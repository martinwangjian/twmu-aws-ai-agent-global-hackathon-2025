# Troubleshooting Guide

Common issues and solutions.

## Agent Issues

### Agent Hallucinating Tool Responses

**Problem**: Agent confirms actions (bookings, API calls) but nothing actually happens.

**Example**: Agent says "Booking confirmed! Event ID: abc123" but no calendar event created.

**Root Cause**: Vague system prompt allows LLM to fabricate responses instead of calling tools.

**Solution**: Use explicit workflow prompts with:

1. Numbered mandatory steps
2. Concrete examples with exact parameters
3. Multiple "NEVER fabricate" prohibitions
4. "ALWAYS wait for [tool] response" enforcement

**See**: [A2A Booking Hallucination Fix](../troubleshooting/A2A_BOOKING_HALLUCINATION_FIX.md)

**Verification**:

```bash
# Check if tool was actually called
aws logs filter-log-events \
  --log-group-name /aws/lambda/[YourFunction] \
  --filter-pattern "[toolName]" \
  --region us-east-1
```

---

## Deployment Issues

### AgentCore: "Runtime already exists"

**Problem**: AgentCore runtime already deployed

**Solution**:

```bash
# Option 1: Use existing runtime
cat .agentcore-runtime-arn

# Option 2: Delete and redeploy
./scripts/cleanup.sh
./scripts/deploy.sh
```

### CDK: "Stack already exists"

**Problem**: CloudFormation stack in failed state

**Solution**:

```bash
cd cdk_infra
uv run cdk destroy WhatsAppStack --force
cd ..
./scripts/deploy.sh
```

### AWS Credentials Expired

**Problem**: `ExpiredToken` error

**Solution**:

```bash
# Update .env with new credentials
nano .env

# Reload environment
source .env

# Verify
aws sts get-caller-identity
```

## Runtime Issues

### Lambda: No response from WhatsApp

**Check 1**: Lambda logs

```bash
aws logs tail /aws/lambda/<lambda-name> --follow
```

**Check 2**: SNS subscription

```bash
aws sns list-subscriptions-by-topic \
  --topic-arn <sns-topic-arn>
```

**Check 3**: Event destination

```bash
aws socialmessaging get-linked-whatsapp-business-account \
  --id <waba-id>
```

### AgentCore: Invocation fails

**Check logs**:

```bash
aws logs tail /aws/bedrock-agentcore/runtimes/<runtime-name> --follow
```

**Common causes**:

- Invalid session ID (must be 33+ characters)
- Bedrock permissions missing
- Model not available in region

### WhatsApp: Messages not marked as read

**Check**: Phone number ID format

```bash
# Should be ARN format
arn:aws:social-messaging:us-east-1:...:phone-number-id/...
```

**Fix**: Update Lambda environment variable

## Development Issues

### uv: Command not found

**Solution**:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart shell
exec $SHELL
```

### Pre-commit: Hooks failing

**Solution**:

```bash
# Update hooks
uv run pre-commit autoupdate

# Run manually
uv run pre-commit run --all-files

# Skip if urgent (not recommended)
git commit --no-verify
```

### Tests: Import errors

**Solution**:

```bash
# Sync dependencies
uv sync --all-extras

# Verify installation
uv run pytest --version
```

## Performance Issues

### Lambda: Cold starts

**Solution**:

- Increase memory (faster CPU)
- Use provisioned concurrency
- Optimize dependencies

### AgentCore: Slow responses

**Check**:

- Bedrock model latency
- MCP tool performance
- Network latency

## Security Issues

### Secrets: Not found

**Check Secrets Manager**:

```bash
aws secretsmanager get-secret-value \
  --secret-id whatsapp-booking/credentials
```

**Create if missing**:

```bash
aws secretsmanager create-secret \
  --name whatsapp-booking/credentials \
  --secret-string '{"key":"value"}'
```

### IAM: Access denied

**Check role policies**:

```bash
aws iam get-role-policy \
  --role-name <role-name> \
  --policy-name <policy-name>
```

## Getting Help

### Check Logs

1. **Lambda logs**: CloudWatch Logs
2. **AgentCore logs**: Bedrock AgentCore logs
3. **CDK logs**: CloudFormation events

### Enable Debug Logging

```bash
# Lambda
aws lambda update-function-configuration \
  --function-name <name> \
  --environment Variables={LOG_LEVEL=DEBUG}
```

### X-Ray Tracing

AWS Console → X-Ray → Service Map

### Contact Support

- GitHub Issues: [repository-url]/issues
- Team: Teamwork Mauritius

---

**Related**:

- [Deployment Guide](deployment.md)
- [Testing Guide](testing.md)
- [Architecture Overview](../architecture/overview.md)
