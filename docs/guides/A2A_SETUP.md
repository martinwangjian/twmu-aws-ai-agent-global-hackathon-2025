# A2A Setup Guide

**Audience**: Developers using Claude Desktop
**Time**: 2 minutes
**Prerequisites**: AgentCore deployed, Claude Desktop installed

## Overview

A2A (Agent-to-Agent) protocol enables Claude Desktop to communicate with your AgentCore agent using MCP (Model Context Protocol).

## Quick Setup

```bash
# 1. Get 60-day refresh token
./scripts/get_refresh_token_direct.sh

# 2. Update Claude Desktop config
./scripts/update-claude-config.sh

# 3. Restart Claude Desktop

# 4. Test (optional)
uv run python scripts/test_refresh_token.py
```

## Authentication: Refresh Token vs Password

### Refresh Token (Recommended) ✅

**Benefits:**

- 🔐 60-day validity (vs 1-hour ID token)
- 🚫 No AWS credentials needed
- 🔄 Auto-refresh with 5-minute buffer
- 🔒 More secure (can't be used directly for API calls)

**Setup:**

```bash
./scripts/get_refresh_token_direct.sh
```

### Password Auth (Legacy)

**Drawbacks:**

- ⏰ 1-hour token expiration
- 🔑 Requires AWS credentials in environment
- 🔄 Manual token updates needed

## How It Works

### 1. Token Acquisition

```bash
# get_refresh_token_direct.sh
aws cognito-idp initiate-auth \
  --client-id qli2ric7jaush0pjstogu4vua \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME=a2a-client,PASSWORD=A2AClient2025! \
  --region us-east-1
```

Saves `COGNITO_REFRESH_TOKEN` to `.env` (valid 60 days).

### 2. Claude Config Update

```bash
# update-claude-config.sh
# Creates ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "a2a-orchestrator": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/project", "python", "mcp_server/a2a_orchestrator_mcp.py"],
      "env": {
        "AWS_REGION": "us-east-1",
        "A2A_AGENT_URL": "https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3A.../invocations/",
        "COGNITO_CLIENT_ID": "qli2ric7jaush0pjstogu4vua",
        "COGNITO_REFRESH_TOKEN": "eyJjdHk..."
      }
    }
  }
}
```

### 3. Auto-Refresh

```python
# mcp_server/a2a_orchestrator_mcp.py
def get_cognito_token() -> str:
    """Get Cognito token with automatic refresh."""
    # Check cache (5-minute buffer)
    if token_valid():
        return cached_token

    # Refresh using refresh token
    cognito = boto3.client("cognito-idp")
    response = cognito.initiate_auth(
        ClientId=client_id,
        AuthFlow="REFRESH_TOKEN_AUTH",
        AuthParameters={"REFRESH_TOKEN": refresh_token},
    )
    return response["AuthenticationResult"]["IdToken"]
```

## Testing

### Test Authentication

```bash
uv run python scripts/test_refresh_token.py
```

Expected output:

```
✅ Successfully obtained token (length: 979)
Token preview: eyJraWQiOiJBMndDb3B6MmlBSTBXV2Yzb2swczAweUVsZWtSRl...
```

### Test A2A Communication

In Claude Desktop:

```
Can you check my bookings?
```

Claude will use the MCP tool to communicate with your agent.

## Troubleshooting

### Token expired (after 60 days)

```bash
# Get new refresh token
./scripts/get_refresh_token_direct.sh

# Update config
./scripts/update-claude-config.sh

# Restart Claude Desktop
```

### "COGNITO_REFRESH_TOKEN not set"

```bash
# Check .env
grep COGNITO_REFRESH_TOKEN .env

# If missing, run:
./scripts/get_refresh_token_direct.sh
```

### "COGNITO_CLIENT_ID not set"

```bash
# Add to .env
echo "COGNITO_CLIENT_ID=qli2ric7jaush0pjstogu4vua" >> .env
```

### Claude Desktop not connecting

1. Check config file exists:

   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. Verify URL encoding (forward slash as `%2F`):

   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq -r '.mcpServers."a2a-orchestrator".env.A2A_AGENT_URL'
   ```

3. Check logs:
   ```bash
   # macOS
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

## Security Notes

- ✅ Refresh token stored in `.env` (gitignored)
- ✅ Token can't be used directly for API calls
- ✅ Auto-refresh prevents token exposure
- ⚠️ Keep `.env` secure (contains refresh token)
- ⚠️ Refresh token valid for 60 days (rotate regularly)

## Architecture

```
Claude Desktop
    ↓ stdio (MCP Protocol)
mcp_server/a2a_orchestrator_mcp.py
    ↓ get_cognito_token() → Cognito ID Token
    ↓ HTTPS + Bearer Token
AgentCore Runtime
    ↓
Strands Agent
```

## References

- [A2A Protocol Spec](https://github.com/aws/a2a-protocol)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [AWS Official Example](https://github.com/awslabs/amazon-bedrock-agentcore-samples/blob/main/01-tutorials/01-AgentCore-runtime/05-hosting-a2a/01-a2a-getting-started-agentcore-strands.ipynb)
