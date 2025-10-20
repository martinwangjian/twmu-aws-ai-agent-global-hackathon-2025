# Restaurant Agent MCP Server for Claude Desktop

Expose the A2A restaurant booking agent as tools in Claude Desktop.

## Quick Setup

### 1. Install Dependencies

```bash
uv pip install mcp httpx
```

### 2. Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "restaurant-booking": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "/Users/martinwang/workspace/TWMU/gen_ai/whatsapp-bot/aws-ai-agent-global-hackathon-2025/mcp_server/restaurant_agent_mcp.py"
      ]
    }
  }
}
```

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 3. Restart Claude Desktop

The restaurant agent tools will appear in Claude Desktop.

## Available Tools

1. **check_availability** - Check table availability
   - Parameters: date, time, party_size

2. **get_menu** - Get menu information
   - Parameters: query (optional)

3. **get_opening_hours** - Get restaurant hours
   - No parameters

4. **create_booking** - Create a reservation
   - Parameters: date, time, party_size, name, phone

## Example Usage in Claude Desktop

```
User: "I want to book dinner at La Bella Vita for 2 people
       next Friday at 7:30 PM. My name is John Smith,
       phone +230-5123-4567"

Claude will:
1. Use check_availability tool
2. Use get_menu tool (if asked)
3. Use create_booking tool
4. Provide confirmation
```

## Demo Scenario

Try this in Claude Desktop:

```
"Help me plan a romantic dinner in Mauritius.
I need a table for 2 next Friday at 7:30 PM.
What vegetarian options do they have?
My name is Jane Doe, phone +230-5999-9999"
```

Claude will orchestrate multiple tool calls to:

- Check availability
- Get menu with vegetarian options
- Confirm opening hours
- Create the booking

## Architecture

```
Claude Desktop
    ↓ (MCP Protocol)
Restaurant Agent MCP Server
    ↓ (A2A Protocol)
Restaurant Booking Agent (ECS)
    ↓
AgentCore Runtime
    ↓
Calendar + Knowledge Base
```

## Benefits

- **Natural Language**: Just talk to Claude naturally
- **Multi-Step**: Claude orchestrates multiple tool calls
- **Context Aware**: Claude maintains conversation context
- **Easy Integration**: No code needed, just configure

## Troubleshooting

**Tools not appearing?**

- Check Claude Desktop logs: `~/Library/Logs/Claude/mcp*.log`
- Verify file path in config is absolute
- Ensure `uv` is in PATH

**Connection errors?**

- Verify agent is deployed: `curl https://restaurant-booking-agent.teamwork-mu.net/.well-known/agent-card.json`
- Check network connectivity

## Testing Locally

```bash
# Test the MCP server
cd mcp_server
uv run python restaurant_agent_mcp.py
```

Then use MCP Inspector or Claude Desktop to test.
