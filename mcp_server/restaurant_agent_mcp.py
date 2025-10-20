#!/usr/bin/env python3
"""
MCP Server for Restaurant Booking Agent

Exposes the A2A restaurant agent as tools for Claude Desktop.
"""

import asyncio

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Configuration
AGENT_URL = "https://restaurant-booking-agent.teamwork-mu.net"
TIMEOUT = 60

# Create MCP server
app = Server("restaurant-booking-agent")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available restaurant agent tools."""
    return [
        Tool(
            name="check_availability",
            description="Check table availability at La Bella Vita restaurant",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date (e.g., 'Friday', '2024-10-17')",
                    },
                    "time": {"type": "string", "description": "Time (e.g., '7:30 PM')"},
                    "party_size": {"type": "integer", "description": "Number of guests"},
                },
                "required": ["date", "time", "party_size"],
            },
        ),
        Tool(
            name="get_menu",
            description="Get restaurant menu and dish information",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Menu query (e.g., 'vegetarian options', 'seafood')",
                    }
                },
            },
        ),
        Tool(
            name="get_opening_hours",
            description="Get restaurant opening hours",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="create_booking",
            description="Create a restaurant booking",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Booking date"},
                    "time": {"type": "string", "description": "Booking time"},
                    "party_size": {"type": "integer", "description": "Number of guests"},
                    "name": {"type": "string", "description": "Customer name"},
                    "phone": {"type": "string", "description": "Contact phone"},
                },
                "required": ["date", "time", "party_size", "name", "phone"],
            },
        ),
    ]


async def call_agent(prompt: str) -> str:
    """Call the A2A restaurant agent."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Simple HTTP call to agent (A2A protocol details abstracted)
        response = await client.post(
            f"{AGENT_URL}/a2a/v1/messages",
            json={
                "kind": "message",
                "role": "user",
                "parts": [{"kind": "text", "text": prompt}],
                "message_id": "mcp-request",
            },
        )

        if response.status_code == 200:
            data = response.json()
            # Extract text from response
            if isinstance(data, dict) and "parts" in data:
                text_parts = [p.get("text", "") for p in data["parts"] if p.get("kind") == "text"]
                return " ".join(text_parts)
            return str(data)

        return f"Error: {response.status_code}"


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "check_availability":
        prompt = (
            f"Is there a table available for {arguments['party_size']} people "
            f"on {arguments['date']} at {arguments['time']}?"
        )

    elif name == "get_menu":
        query = arguments.get("query", "")
        prompt = f"What's on the menu? {query}" if query else "What's on the menu?"

    elif name == "get_opening_hours":
        prompt = "What are your opening hours?"

    elif name == "create_booking":
        prompt = (
            f"Book a table for {arguments['party_size']} people "
            f"on {arguments['date']} at {arguments['time']}. "
            f"Name: {arguments['name']}, Phone: {arguments['phone']}"
        )

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    # Call the agent
    result = await call_agent(prompt)

    return [TextContent(type="text", text=result)]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
