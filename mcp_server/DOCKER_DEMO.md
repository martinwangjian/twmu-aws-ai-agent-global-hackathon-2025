# A2A Orchestrator MCP Server - Docker Demo

Reproducible demo setup for hackathon presentations.

## Quick Start

### 1. Build Docker Image

```bash
cd mcp_server
docker build -t a2a-orchestrator-mcp .
```

### 2. Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "a2a-orchestrator": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "a2a-orchestrator-mcp"]
    }
  }
}
```

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 3. Restart Claude Desktop

### 4. Test the Demo

In Claude Desktop, say:

```
"Plan a trip to Mauritius with dinner for 2 people
next Friday at 7:30 PM. I want vegetarian options.
My name is Jane Doe, phone +230-5999-9999"
```

## What Happens

1. **Claude** calls the `plan_trip` tool
2. **MCP Server** (in Docker) receives the request
3. **Strands Agent** discovers A2A agents
4. **A2A Protocol** communicates with restaurant agent
5. **Response** flows back to Claude

## Architecture

```
Claude Desktop
    ↓ (MCP Protocol)
Docker Container
    ├─ MCP Server
    └─ Strands Agent with A2A Tools
         ↓ (A2A Protocol)
Restaurant Agent (ECS)
    ↓
AgentCore Runtime
```

## Benefits

✅ **Reproducible** - Same environment everywhere
✅ **Isolated** - No dependency conflicts
✅ **Portable** - Works on any platform with Docker
✅ **Demo Ready** - Perfect for hackathon presentations

## Troubleshooting

### Check Docker logs

```bash
docker logs a2a-orchestrator-mcp
```

### Test manually

```bash
docker run -i --rm a2a-orchestrator-mcp
```

### Rebuild after changes

```bash
docker build --no-cache -t a2a-orchestrator-mcp .
```

## For Hackathon Judges

This demo shows:

- ✅ A2A agent discovery via `.well-known/agent-card.json`
- ✅ Multi-agent orchestration using Strands framework
- ✅ Real production deployment (ECS Fargate)
- ✅ Standard protocols (A2A, MCP)
- ✅ Zero-code integration with Claude Desktop

## Alternative: Docker Compose

```bash
docker-compose up -d
```

Then configure Claude to use:

```json
{
  "mcpServers": {
    "a2a-orchestrator": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "a2a-orchestrator-mcp",
        "python",
        "a2a_orchestrator_mcp.py"
      ]
    }
  }
}
```
