# A2A Agent Deployment Guide

**Architecture**: Option 3 - Separate A2A Agent on ECS with Gateway Tools

## Prerequisites

- ✅ AWS credentials configured (us-east-1)
- ✅ AgentCore Gateway deployed (`gateway_config.json` exists)
- ✅ Calendar Lambda deployed
- ✅ Docker installed (for MCP server rebuild)
- ✅ Claude Desktop with MCP configured

## Deployment Steps

### 1. Refresh AWS Credentials

```bash
# If using temporary credentials
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...

# Or use AWS SSO
aws sso login --profile your-profile
```

### 2. Deploy A2A Agent Stack

```bash
./scripts/deploy-a2a-agent.sh
```

**Expected Output**:

```
✅ A2AAgentStack

Outputs:
A2AAgentStack.LoadBalancerDNS = A2AAg-A2ASe-xxxxx.us-east-1.elb.amazonaws.com
A2AAgentStack.A2AAgentURL = http://A2AAg-A2ASe-xxxxx.us-east-1.elb.amazonaws.com
A2AAgentStack.AgentCardURL = http://A2AAg-A2ASe-xxxxx.us-east-1.elb.amazonaws.com/.well-known/agent-card.json
```

### 3. Verify Agent Card

```bash
# Replace with your ALB DNS
curl http://A2AAg-A2ASe-xxxxx.us-east-1.elb.amazonaws.com/.well-known/agent-card.json
```

**Expected Response**:

```json
{
  "name": "La Bella Vita Restaurant Agent",
  "description": "Restaurant booking and information agent for La Bella Vita in Mauritius",
  "version": "0.0.1",
  "protocolVersion": "1.0.0",
  "skills": [...]
}
```

### 4. Update MCP Server

```bash
# Set A2A agent URL
export A2A_AGENT_URL=http://A2AAg-A2ASe-xxxxx.us-east-1.elb.amazonaws.com

# Rebuild MCP Docker image
docker build -f Dockerfile.a2a -t a2a-orchestrator-mcp .
```

### 5. Update Claude Desktop MCP Config

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "a2a-orchestrator": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "A2A_AGENT_URL=http://A2AAg-A2ASe-xxxxx.us-east-1.elb.amazonaws.com",
        "a2a-orchestrator-mcp"
      ]
    }
  }
}
```

### 6. Restart Claude Desktop

```bash
# macOS
killall Claude && open -a Claude

# Or manually quit and reopen
```

## Testing

### Test 1: Agent Discovery

**Prompt**: "What agents are available?"

**Expected**: Claude should discover "La Bella Vita Restaurant Agent"

### Test 2: Restaurant Discovery

**Prompt**: "Find Italian restaurants in Mauritius with vegetarian options"

**Expected**: Mock restaurant list (La Bella Vita, Trattoria Romana, Il Giardino)

### Test 3: Booking Flow

**Prompt**: "Book a table at La Bella Vita for 2 people tomorrow at 7pm"

**Expected Steps**:

1. Claude calls `discover_restaurants` tool
2. Claude calls `book_restaurant` tool
3. A2A agent checks availability via Gateway
4. A2A agent creates calendar event via Gateway
5. Claude receives booking confirmation with event ID

**Success Criteria**:

- ✅ No fabricated responses
- ✅ Actual calendar event created
- ✅ Event ID returned in confirmation
- ✅ No "Response ended prematurely" errors

### Test 4: Verify Calendar Event

```bash
# Check Google Calendar via Gateway
# (or check calendar directly in Google Calendar UI)
```

## Troubleshooting

### Issue: "Connection refused"

**Cause**: ECS task not healthy yet

**Solution**: Wait 1-2 minutes for task to start, check health:

```bash
curl http://A2AAg-A2ASe-xxxxx.us-east-1.elb.amazonaws.com/health
```

### Issue: "Agent card not found"

**Cause**: A2A server not serving agent card

**Solution**: Check ECS logs:

```bash
aws logs tail /ecs/a2a-agent --follow
```

### Issue: "Gateway authentication failed"

**Cause**: OAuth token expired or invalid

**Solution**: Check `gateway_config.json` credentials are correct

### Issue: "No response from agent"

**Cause**: Agent crashed or Gateway tools not loaded

**Solution**: Check ECS logs for errors:

```bash
aws logs tail /ecs/a2a-agent --follow
```

## Architecture Validation

### Verify Separate Paths

**WhatsApp Path** (unchanged):

```
WhatsApp → SNS → Lambda → AgentCore Runtime
```

**A2A Path** (new):

```
Claude → MCP → ECS A2A Agent → Gateway → Calendar Lambda
```

### Verify No Fabrication

Check CloudWatch logs for A2A agent:

```bash
aws logs tail /ecs/a2a-agent --follow
```

**Look for**:

- ✅ Gateway tool calls (checkAvailability, createEvent)
- ✅ Actual responses from Gateway
- ❌ No "fabricating response" messages
- ❌ No empty responses (0 chars)

## Monitoring

### CloudWatch Logs

**A2A Agent Logs**:

```bash
aws logs tail /ecs/a2a-agent --follow
```

**ALB Access Logs** (if enabled):

```bash
aws logs tail /aws/elasticloadbalancing/app/A2AAg-A2ASe-xxxxx --follow
```

### Metrics

**ECS Service**:

- CPU utilization
- Memory utilization
- Task count

**ALB**:

- Request count
- Target response time
- Healthy host count

## Cost Estimate

**ECS Fargate**:

- 1 task × 256 CPU × 512 MB = ~$10/month
- Auto-scaling to 3 tasks = ~$30/month max

**ALB**:

- ~$16/month base + data transfer

**Total**: ~$26-46/month

## Cleanup

To remove A2A agent stack:

```bash
cd cdk_infra
uv run cdk destroy A2AAgentStack
```

## Next Steps

1. ✅ Deploy to production
2. ⏳ Add HTTPS with ACM certificate
3. ⏳ Configure custom domain (Route53)
4. ⏳ Enable ALB access logs
5. ⏳ Set up CloudWatch alarms
6. ⏳ Implement rate limiting

## References

- [A2A Implementation Plan](../architecture/A2A_SEPARATE_AGENT_PLAN.md)
- [Architecture Review](../ARCHITECTURE_REVIEW.md)
- [Strands A2A Documentation](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/)
