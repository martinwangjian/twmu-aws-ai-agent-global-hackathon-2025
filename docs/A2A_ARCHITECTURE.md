# A2A Architecture

## Current Implementation

### Why agentRuntimeArn is Required

**Current Flow:**

```
MCP Server → boto3 → AgentCore Runtime → Booking Agent
```

The `agentRuntimeArn` is an **AWS-specific implementation detail**, not an A2A protocol requirement. We use it because:

1. Our booking agent is deployed on AWS Bedrock AgentCore
2. The MCP server calls AgentCore Runtime via boto3 SDK
3. This requires AWS credentials and the runtime ARN

**Problem:** This violates A2A protocol principles - orchestrators shouldn't need AWS credentials to call A2A agents.

### Proposed Architecture

**New Flow:**

```
MCP Server → HTTP/JSON-RPC → A2A Proxy → AgentCore Runtime → Booking Agent
```

**Benefits:**

- MCP server uses standard A2A protocol (HTTP + JSON-RPC)
- No AWS credentials needed in orchestrator
- True protocol compliance
- Works with any A2A client

## A2A Protocol Compliance

### Agent Card Discovery

- Endpoint: `/.well-known/agent-card.json`
- Returns: Agent metadata, skills, capabilities

### Message Exchange

- Endpoint: `/a2a/v1` (JSON-RPC 2.0)
- Method: `POST` with JSON-RPC envelope
- No authentication required (public demo)

### Progressive Disclosure

- Skills accept optional parameters
- Orchestrators can refine requests iteratively
- Example: Check availability without time → get timeslots → book specific slot

## Implementation Changes

1. **Remove boto3 from MCP server** - Use httpx for A2A calls
2. **Add JSON schemas to agent card** - Define required/optional fields
3. **Update A2A proxy** - Handle optional parameters gracefully
4. **Add new skills** - location, policies, modify-booking
