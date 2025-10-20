# A2A Agent Discovery Demo for Claude Desktop

Demonstrates agent discovery and orchestration using the A2A protocol.

## Setup

### 1. Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "a2a-orchestrator": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/Users/martinwang/workspace/TWMU/gen_ai/whatsapp-bot/aws-ai-agent-global-hackathon-2025/mcp_server/a2a_orchestrator_mcp.py"
      ]
    }
  }
}
```

### 2. Restart Claude Desktop

## Demo Scenario

### Step 1: Discover Agents

```
User: "Discover available restaurant agents"

Claude uses: discover_agents(domain="restaurant")

Result:
🔍 Found: La Bella Vita Restaurant Agent
   • 7 skills available
   • A2A protocol v1.0.0
```

### Step 2: Plan Trip

```
User: "Plan a romantic dinner in Mauritius for 2 people next Friday"

Claude uses: plan_trip(
  destination="Mauritius",
  requirements="romantic dinner for 2, Friday"
)

Result:
🌴 Trip planning initiated
🔍 Discovered restaurant agent
💡 Suggested next steps
```

### Step 3: Call Agent

```
User: "Check if they have availability for 2 people Friday at 7:30 PM"

Claude uses: call_agent(
  agent_name="La Bella Vita Restaurant Agent",
  request="Check availability for 2 people Friday 7:30 PM"
)

Result:
📤 Request sent via A2A protocol
📥 Response from agent
```

### Step 4: Get Details

```
User: "What vegetarian options do they have?"

Claude uses: call_agent(
  agent_name="La Bella Vita Restaurant Agent",
  request="What vegetarian options are available?"
)
```

### Step 5: Make Booking

```
User: "Book it! My name is Jane Doe, phone +230-5999-9999"

Claude uses: call_agent(
  agent_name="La Bella Vita Restaurant Agent",
  request="Book table for 2, Friday 7:30 PM, Jane Doe, +230-5999-9999"
)

Result:
✅ Booking confirmed
📋 Confirmation number provided
```

## Complete Demo Flow

Try this in Claude Desktop:

```
"I'm planning a trip to Mauritius and need to book a romantic dinner.
Can you discover available restaurant agents and help me make a
reservation for 2 people next Friday at 7:30 PM?
I'd like to know about vegetarian options.
My name is John Smith, phone +230-5123-4567"
```

Claude will:

1. ✅ Discover agents (A2A protocol)
2. ✅ Plan the trip
3. ✅ Check availability
4. ✅ Get menu info
5. ✅ Create booking
6. ✅ Provide confirmation

## Key Features Demonstrated

### 1. Agent Discovery

- Uses A2A `.well-known/agent-card.json` endpoint
- Lists agent capabilities (7 skills)
- Shows protocol version

### 2. Multi-Agent Orchestration

- Planner coordinates with discovered agents
- Natural language to A2A protocol translation
- Context maintained across calls

### 3. Real A2A Protocol

- Actual HTTP calls to deployed agent
- Standard A2A message format
- Production-ready integration

## Architecture

```
Claude Desktop
    ↓
MCP Protocol
    ↓
Orchestrator MCP Server
    ├─→ discover_agents (A2A discovery)
    ├─→ plan_trip (coordination)
    └─→ call_agent (A2A messages)
         ↓
    A2A Protocol
         ↓
Restaurant Agent (ECS)
         ↓
AgentCore Runtime
```

## Benefits

- **Zero Code**: User just talks to Claude naturally
- **Agent Discovery**: Automatic capability detection
- **Protocol Standard**: Uses A2A spec
- **Extensible**: Easy to add more agents
- **Production Ready**: Real deployed agent

## Testing

```bash
# Test locally
cd mcp_server
uv run python a2a_orchestrator_mcp.py
```

## Troubleshooting

Check Claude logs:

```bash
tail -f ~/Library/Logs/Claude/mcp*.log
```

Verify agent is accessible:

```bash
curl https://restaurant-booking-agent.teamwork-mu.net/.well-known/agent-card.json
```
