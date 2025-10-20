# Claude Desktop Setup for A2A Agent

## Step 1: Copy Config

```bash
# Copy the config to Claude Desktop
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

## Step 2: Set AWS Credentials

Make sure AWS credentials are in your environment:

```bash
# Check credentials
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
echo $AWS_SESSION_TOKEN

# If not set, source .env
source .env
```

## Step 3: Restart Claude Desktop

```bash
# Kill Claude
killall Claude

# Start Claude
open -a Claude
```

## Step 4: Test

In Claude Desktop, try:

**Test 1: Discovery**

```
What agents are available?
```

**Test 2: Restaurant Discovery**

```
Find Italian restaurants in Mauritius with vegetarian options
```

**Test 3: Booking**

```
Book a table at La Bella Vita for 2 people tomorrow at 7pm
```

## Troubleshooting

### Issue: "No MCP servers found"

- Check config file location
- Restart Claude Desktop

### Issue: "AWS credentials not found"

- Export credentials in terminal before starting Claude
- Or add to shell profile (~/.zshrc or ~/.bashrc)

### Issue: "Agent not responding"

- Check Docker is running
- Check MCP Docker image exists: `docker images | grep a2a-orchestrator-mcp`
- Check agent is deployed: `uv run agentcore status`

## Current Setup

**Agent**: `agentcore_a2a_server-vlipXVAdx7`
**Protocol**: A2A (JSON-RPC)
**Auth**: IAM SigV4 (uses AWS credentials)
**Tools**: 5 calendar tools (checkAvailability, createEvent, deleteEvent, getAvailableSlots, listEvents)

## Next: Add Cognito (Optional)

For production with external users, add Cognito OAuth:

1. Create Cognito user pool (CDK)
2. Configure agent with JWT authorizer
3. Redeploy agent
4. Update MCP server to use bearer token
