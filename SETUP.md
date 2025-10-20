# Setup Instructions

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- AWS Account with Bedrock access
- AWS CLI configured
- Node.js 18+ (for CDK)

## Configuration

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd twmu-aws-ai-agent-global-hackathon-2025
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=<your-aws-account-id>

# AgentCore Configuration
A2A_AGENT_URL=https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A<YOUR_AWS_ACCOUNT_ID>%3Aruntime%2F<YOUR_AGENTCORE_RUNTIME_ID>/invocations/

# Cognito Configuration (for A2A authentication)
COGNITO_USER_POOL_ID=us-east-1_<YOUR_USER_POOL_ID>
COGNITO_CLIENT_ID=<YOUR_CLIENT_ID>
COGNITO_REFRESH_TOKEN=<YOUR_REFRESH_TOKEN>

# Session Storage
SESSION_BUCKET=agentcore-sessions-<YOUR_AWS_ACCOUNT_ID>
```

### 3. Install Dependencies

```bash
./scripts/init-dev-env.sh
```

### 4. Deploy Infrastructure

```bash
./scripts/deploy.sh
```

This will:
- Deploy CDK stacks (Cognito, WhatsApp, AgentCore)
- Create necessary AWS resources
- Configure AgentCore runtime
- Set up WhatsApp integration

### 5. Configure Google Calendar (Optional)

If you want calendar integration:

1. Create a Google Cloud project
2. Enable Google Calendar API
3. Create service account credentials
4. Download `service-account-key.json`
5. Place in project root

### 6. Get Cognito Refresh Token

For A2A authentication:

```bash
./scripts/get_refresh_token_direct.sh
```

Follow the prompts to authenticate and get a 60-day refresh token.

### 7. Configure Claude Desktop (Optional)

For A2A testing with Claude Desktop:

```bash
./scripts/update-claude-config.sh
```

Restart Claude Desktop after configuration.

## Testing

### Run All Tests

```bash
uv run pytest
```

### Test WhatsApp Integration

```bash
./scripts/test.sh
```

### Test A2A Protocol

```bash
./scripts/test-a2a.sh
```

## Deployment Verification

After deployment, verify:

1. **AgentCore Runtime**: Check AWS Console → Bedrock → AgentCore
2. **Cognito User Pool**: Check AWS Console → Cognito
3. **Lambda Functions**: Check AWS Console → Lambda
4. **WhatsApp Integration**: Send test message

## Troubleshooting

### AgentCore Runtime Not Found

```bash
aws bedrock-agentcore list-runtimes --region us-east-1
```

### Cognito Authentication Failing

```bash
./scripts/test_refresh_token.py
```

### WhatsApp Not Responding

```bash
./scripts/diagnose_whatsapp.sh
```

## Getting Help

- **Documentation**: See [docs/README.md](docs/README.md)
- **Issues**: Open an issue on GitHub
- **Hackathon**: AWS AI Agent Global Hackathon 2025

## Security Notes

- Never commit `.env` file
- Never commit `service-account-key.json`
- Never commit `gateway_config.json`
- Use AWS Secrets Manager for production
- Rotate credentials regularly

## License

AGPL-3.0 - See [LICENSE](LICENSE) for details
