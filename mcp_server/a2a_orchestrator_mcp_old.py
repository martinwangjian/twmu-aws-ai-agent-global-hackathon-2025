#!/usr/bin/env python3
"""
MCP Server for A2A Agent Discovery Demo

Demonstrates agent discovery and orchestration via Claude Desktop.
"""

import asyncio

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Configuration
AGENT_URL = "https://restaurant-booking-agent.teamwork-mu.net"
TIMEOUT = 60

app = Server("a2a-orchestrator")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List orchestrator tools."""
    return [
        Tool(
            name="discover_agents",
            description="Discover available A2A agents and their capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain to search (e.g., 'restaurant', 'hotel')",
                    }
                },
            },
        ),
        Tool(
            name="plan_trip",
            description="Plan a trip by coordinating with discovered agents",
            inputSchema={
                "type": "object",
                "properties": {
                    "destination": {"type": "string", "description": "Destination"},
                    "requirements": {
                        "type": "string",
                        "description": "Trip requirements (dining, activities, etc.)",
                    },
                },
                "required": ["destination", "requirements"],
            },
        ),
        Tool(
            name="call_agent",
            description="Call a specific discovered agent with a request",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Agent name"},
                    "request": {"type": "string", "description": "Request to send"},
                },
                "required": ["agent_name", "request"],
            },
        ),
    ]


async def discover_restaurant_agent() -> dict:
    """Discover restaurant agent via A2A protocol."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{AGENT_URL}/.well-known/agent-card.json")
        if response.status_code == 200:
            return response.json()
        return {}


async def call_agent(request: str) -> str:
    """Call restaurant agent."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            f"{AGENT_URL}/a2a/v1/messages",
            json={
                "kind": "message",
                "role": "user",
                "parts": [{"kind": "text", "text": request}],
                "message_id": "orchestrator",
            },
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "parts" in data:
                return " ".join(p.get("text", "") for p in data["parts"])
            return str(data)
        return f"Error: {response.status_code}"


@app.call_tool()
async def handle_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "discover_agents":
        domain = arguments.get("domain", "").lower()

        # Mock discovery - only restaurant agent available
        if "restaurant" in domain or not domain:
            agent_card = await discover_restaurant_agent()

            result = f"""🔍 Agent Discovery Results

Found 1 agent matching '{domain or 'all'}':

📍 Agent: {agent_card.get('name', 'Unknown')}
   URL: {AGENT_URL}
   Description: {agent_card.get('description', 'N/A')}
   Protocol: A2A v{agent_card.get('protocolVersion', '1.0.0')}

   Skills ({len(agent_card.get('skills', []))}):
"""
            for skill in agent_card.get("skills", []):
                result += f"   • {skill['id']}: {skill.get('description', 'N/A')}\n"

            result += "\n✅ Use 'call_agent' to interact with this agent"
            return [TextContent(type="text", text=result)]

        return [TextContent(type="text", text=f"❌ No agents found for domain: {domain}")]

    if name == "plan_trip":
        destination = arguments["destination"]
        requirements = arguments["requirements"]

        # Discover agents
        agent_card = await discover_restaurant_agent()

        result = f"""🌴 Trip Planning for {destination}

📋 Requirements: {requirements}

🔍 Step 1: Agent Discovery
   Found: {agent_card.get('name')}
   Capabilities: {len(agent_card.get('skills', []))} skills

🤖 Step 2: Coordinating with agents...
   I'll help coordinate your trip requirements.

   For dining arrangements, I can:
   • Check restaurant availability
   • Get menu information
   • Make reservations
   • Check opening hours

💡 Next: Use 'call_agent' with specific requests like:
   - "Check availability for 2 people Friday 7:30 PM"
   - "What vegetarian options are available?"
   - "Book a table for 2 on Friday at 7:30 PM, name John Smith"
"""
        return [TextContent(type="text", text=result)]

    if name == "call_agent":
        agent_name = arguments["agent_name"]
        request = arguments["request"]

        # Only restaurant agent available
        if "bella vita" in agent_name.lower() or "restaurant" in agent_name.lower():
            response = await call_agent(request)

            result = f"""📤 Request to {agent_name}:
   "{request}"

📥 Response:
   {response}
"""
            return [TextContent(type="text", text=result)]

        return [TextContent(type="text", text=f"❌ Agent not found: {agent_name}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
