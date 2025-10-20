# Environment Variables Reference

All environment variables used in the project.

## AWS Credentials

### `AWS_ACCESS_KEY_ID`

- **Required**: Yes
- **Type**: String
- **Description**: AWS access key ID
- **Example**: `AKIAIOSFODNN7EXAMPLE`

### `AWS_SECRET_ACCESS_KEY`

- **Required**: Yes
- **Type**: String
- **Description**: AWS secret access key
- **Example**: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

### `AWS_SESSION_TOKEN`

- **Required**: For temporary credentials
- **Type**: String
- **Description**: AWS session token
- **Example**: `FwoGZXIvYXdzEBYaD...`

### `AWS_REGION`

- **Required**: Yes
- **Type**: String
- **Default**: `us-east-1`
- **Description**: AWS region for deployment
- **Allowed**: `us-east-1` (tested)

## Application Configuration

### `AGENTCORE_RUNTIME_ARN`

- **Required**: No (auto-detected)
- **Type**: String (ARN)
- **Description**: AgentCore runtime ARN
- **Example**: `arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/agentcore_mcp_agent-xxx`
- **Note**: Auto-saved to `.agentcore-runtime-arn` file

### `WHATSAPP_BUSINESS_ACCOUNT_ID`

- **Required**: No
- **Type**: String
- **Description**: WhatsApp Business Account ID
- **Format**: `waba-{id}`
- **Example**: `waba-ea04858844fa4c68b1248a47be914ea9`

### `BEDROCK_MODEL_ID`

- **Required**: No
- **Type**: String
- **Default**: `us.amazon.nova-pro-v1:0`
- **Description**: Bedrock model ID for LLM
- **Options**:
  - `us.amazon.nova-pro-v1:0` (default)
  - `anthropic.claude-3-sonnet-20240229-v1:0`
  - `anthropic.claude-3-haiku-20240307-v1:0`

## Lambda Configuration

### `LOG_LEVEL`

- **Required**: No
- **Type**: String
- **Default**: `INFO`
- **Description**: Lambda logging level
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`

### `WHATSAPP_SECRET_ARN`

- **Required**: Auto-set by CDK
- **Type**: String (ARN)
- **Description**: Secrets Manager ARN for WhatsApp credentials
- **Example**: `arn:aws:secretsmanager:us-east-1:123456789012:secret:whatsapp-booking/credentials-xxx`

### `WHATSAPP_PHONE_NUMBER_ID`

- **Required**: Auto-detected
- **Type**: String (ARN)
- **Description**: WhatsApp phone number ID ARN
- **Example**: `arn:aws:social-messaging:us-east-1:123456789012:phone-number-id/xxx`

## Development

### `DOCKER_CONTAINER`

- **Required**: No
- **Type**: Boolean
- **Default**: `0`
- **Description**: Set to `1` when running in Docker
- **Used by**: Container builds

## File: `.env.example`

```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_SESSION_TOKEN=your-session-token
AWS_REGION=us-east-1

# Application
WHATSAPP_BUSINESS_ACCOUNT_ID=waba-your-id
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0

# Development
LOG_LEVEL=INFO
```

---

**Related**:

- [Scripts Reference](scripts.md)
- [CDK Stacks](cdk-stacks.md)
- [Deployment Guide](../guides/deployment.md)
