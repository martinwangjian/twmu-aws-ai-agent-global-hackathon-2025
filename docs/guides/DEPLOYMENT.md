# Deployment Guide

**Audience**: Developers, DevOps
**Time**: 10 minutes
**Prerequisites**: AWS account, uv installed

## Quick Deploy

```bash
./scripts/deploy.sh
```

That's it! The script handles everything.

## What Gets Deployed

### 1. AgentCore Runtime

- **Service**: Amazon Bedrock AgentCore
- **Method**: Starter Toolkit
- **Runtime**: `agentcore_mcp_agent`
- **ARN**: Saved to `.agentcore-runtime-arn`

### 2. WhatsApp Stack (CDK)

- **SNS Topic**: `WhatsAppMessages`
- **Lambda**: Message orchestrator
- **Secrets Manager**: WhatsApp credentials
- **Event Destination**: Auto-configured

### 3. A2A Setup (Optional)

For Claude Desktop integration:

```bash
# Get 60-day refresh token
./scripts/get_refresh_token_direct.sh

# Update Claude Desktop config
./scripts/update-claude-config.sh

# Restart Claude Desktop
```

**What this configures:**

- MCP server for A2A orchestration
- Cognito refresh token authentication (60-day validity)
- No AWS credentials needed in Claude config
- Auto-refresh with 5-minute buffer

## Manual Deployment

If you need more control:

### Step 1: Deploy AgentCore

```bash
# Configure
uv run agentcore configure \
  --entrypoint src/agents/agentcore_mcp_agent.py \
  --yes

# Launch
uv run agentcore launch

# Save ARN
aws bedrock-agentcore list-agent-runtimes \
  --region us-east-1 \
  --query "agentRuntimes[?contains(agentRuntimeArn, 'agentcore_mcp_agent')].agentRuntimeArn" \
  --output text > .agentcore-runtime-arn
```

### Step 2: Deploy CDK

```bash
cd cdk_infra
uv run cdk deploy WhatsAppStack --require-approval never
```

## Environment Variables

Set in `.env`:

```bash
# Required
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Optional
WHATSAPP_BUSINESS_ACCOUNT_ID=waba-...
AGENTCORE_RUNTIME_ARN=arn:...
```

## Deployment Outputs

After deployment, you'll see:

```
✅ Deployment complete!

Outputs:
  WhatsAppStack.SNSTopicArn = arn:aws:sns:...
  WhatsAppStack.OrchestratorName = WhatsAppStack-...
  WhatsAppStack.SecretArn = arn:aws:secretsmanager:...
```

## Testing Deployment

```bash
./scripts/test.sh
```

## Updating

To update after code changes:

```bash
# Update Lambda only
cd cdk_infra
uv run cdk deploy WhatsAppStack

# Update AgentCore
uv run agentcore launch
```

## Cleanup

```bash
./scripts/cleanup.sh
```

**Warning**: This deletes all resources!

## Troubleshooting

### AgentCore already exists

```bash
# Check existing
aws bedrock-agentcore list-agent-runtimes --region us-east-1

# Delete and redeploy
./scripts/cleanup.sh
./scripts/deploy.sh
```

### CDK deployment fails

```bash
# Check CloudFormation
aws cloudformation describe-stack-events \
  --stack-name WhatsAppStack \
  --max-items 10

# Force delete
cd cdk_infra
uv run cdk destroy WhatsAppStack --force
```

### Lambda errors

```bash
# Check logs
aws logs tail /aws/lambda/<lambda-name> --follow

# Check X-Ray traces
# AWS Console → X-Ray → Service Map
```

## Related Documentation

- **[Architecture Overview](../architecture/overview.md)**
- **[Testing Guide](testing.md)**
- **[Troubleshooting](troubleshooting.md)**
- **[Scripts Reference](../reference/scripts.md)**

---

**See also**: [DEPLOYMENT_SIMPLIFIED.md](DEPLOYMENT_SIMPLIFIED.md) for detailed script documentation
