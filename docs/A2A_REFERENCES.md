# A2A Implementation References

## Authentication

### Cognito Refresh Token (Recommended)

**Benefits:**

- 🔐 60-day validity (vs 1-hour ID token)
- 🚫 No AWS credentials needed in Claude config
- 🔄 Auto-refresh with 5-minute buffer
- 🔒 More secure (refresh token can't be used directly for API calls)

**Setup:**

```bash
# 1. Get refresh token (one-time, valid 60 days)
./scripts/get_refresh_token_direct.sh

# 2. Update Claude Desktop config
./scripts/update-claude-config.sh

# 3. Restart Claude Desktop

# 4. Test authentication
uv run python scripts/test_refresh_token.py
```

**Implementation:**

```python
def get_cognito_token() -> str:
    """Get Cognito token with automatic refresh using refresh token."""
    cognito = boto3.client("cognito-idp", region_name=region)
    response = cognito.initiate_auth(
        ClientId=client_id,
        AuthFlow="REFRESH_TOKEN_AUTH",
        AuthParameters={"REFRESH_TOKEN": refresh_token},
    )
    return response["AuthenticationResult"]["IdToken"]
```

## AWS Official Examples

The A2A implementation is based on the official AWS AgentCore samples repository.

### Primary Reference

**Repository**: [awslabs/amazon-bedrock-agentcore-samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples)

**Key Example**: `01-tutorials/01-AgentCore-runtime/05-hosting-a2a/01-a2a-getting-started-agentcore-strands.ipynb`

**Direct Link**: [View on GitHub](https://github.com/awslabs/amazon-bedrock-agentcore-samples/blob/main/01-tutorials/01-AgentCore-runtime/05-hosting-a2a/01-a2a-getting-started-agentcore-strands.ipynb)

### What the Example Demonstrates

1. **Agent Card Discovery**: AgentCore Runtime DOES serve agent cards at `/.well-known/agent-card.json`
2. **Authentication**: Bearer token (Cognito ID token) passed in Authorization header
3. **URL Format**: `https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{escaped_arn}/invocations/`
4. **A2A Client Usage**: Use `A2ACardResolver` to fetch agent card, then create client with factory

### Key Code Pattern

```python
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, Role, TextPart
import httpx
from uuid import uuid4

# Setup authentication headers
headers = {
    "Authorization": f"Bearer {bearer_token}",
    "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id
}

# Create HTTP client with auth headers
async with httpx.AsyncClient(timeout=300, headers=headers) as httpx_client:
    # Fetch agent card from AgentCore Runtime
    resolver = A2ACardResolver(httpx_client=httpx_client, base_url=runtime_url)
    agent_card = await resolver.get_agent_card()

    # Create A2A client
    config = ClientConfig(httpx_client=httpx_client, streaming=False)
    factory = ClientFactory(config)
    client = factory.create(agent_card)

    # Send message
    msg = Message(
        kind="message",
        role=Role.user,
        parts=[Part(TextPart(kind="text", text=message))],
        message_id=uuid4().hex,
    )

    async for event in client.send_message(msg):
        # Process response
        pass
```

## Important Findings

### Agent Card Availability

**Myth**: AgentCore Runtime doesn't serve agent cards
**Reality**: AgentCore Runtime with `server_protocol: A2A` DOES serve agent cards at `/invocations/.well-known/agent-card.json`

**Requirements**:

1. Must provide Bearer token in Authorization header
2. **CRITICAL**: ARN must be FULLY URL encoded including forward slashes (`/` → `%2F`)
3. Session ID must be at least 33 characters long

### URL Encoding Issue

**Wrong** (causes 404):

```
https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A445567080739%3Aruntime/agentcore_a2a_server-vlipXVAdx7/invocations/
```

Note: The `/` before `agentcore_a2a_server` is NOT encoded

**Correct** (works):

```
https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A445567080739%3Aruntime%2Fagentcore_a2a_server-vlipXVAdx7/invocations/
```

Note: ALL characters encoded, including `/` → `%2F`

### Session ID Requirement

**Wrong** (causes validation error):

```
X-Amzn-Bedrock-AgentCore-Runtime-Session-Id: test-session-123
```

**Correct** (works):

```
X-Amzn-Bedrock-AgentCore-Runtime-Session-Id: test-session-123456789012345678901234567890123
```

Minimum length: 33 characters

### Testing with curl

```bash
# Get Cognito token
TOKEN=$(python3 << 'EOF'
import boto3
cognito = boto3.client("cognito-idp", region_name="us-east-1")
response = cognito.initiate_auth(
    ClientId="qli2ric7jaush0pjstogu4vua",
    AuthFlow="USER_PASSWORD_AUTH",
    AuthParameters={"USERNAME": "a2a-client", "PASSWORD": "A2AClient2025!"}
)
print(response["AuthenticationResult"]["IdToken"])
EOF
)

# Test agent card endpoint
curl -H "Authorization: Bearer $TOKEN" \
  -H "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id: $(uuidgen)$(uuidgen)" \
  "https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A445567080739%3Aruntime%2Fagentcore_a2a_server-vlipXVAdx7/invocations/.well-known/agent-card.json"
```

### URL Format

The runtime URL must include `/invocations/`:

```
https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/{url_encoded_arn}/invocations/
```

The agent card is then available at:

```
{runtime_url}/.well-known/agent-card.json
```

### Authentication

- Use Cognito **ID token** (not access token)
- Pass in `Authorization: Bearer {token}` header
- Include session ID in `X-Amzn-Bedrock-AgentCore-Runtime-Session-Id` header

## Our Implementation

File: `mcp_server/a2a_orchestrator_mcp.py`

Our implementation follows the AWS example pattern:

1. Get Cognito ID token (with auto-refresh)
2. Create httpx client with auth headers
3. Use A2ACardResolver to fetch agent card
4. Create A2A client with ClientFactory
5. Send messages using A2A protocol

## Related Documentation

- [A2A Final Architecture](A2A_FINAL_ARCHITECTURE.md)
- [A2A AP2 Demo Guide](A2A_AP2_DEMO.md)
- [Strands A2A Documentation](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/)
