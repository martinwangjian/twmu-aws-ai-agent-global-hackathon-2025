#!/usr/bin/env python3
"""Test the MCP server locally."""

import asyncio
import sys

sys.path.insert(
    0,
    "/Users/martinwang/workspace/TWMU/gen_ai/whatsapp-bot/aws-ai-agent-global-hackathon-2025/mcp_server",
)

from restaurant_agent_mcp import call_tool, list_tools


async def main():
    """Test MCP server functions."""
    print("🧪 Testing Restaurant Agent MCP Server\n")

    # Test 1: List tools
    print("1️⃣ Listing available tools...")
    tools = await list_tools()
    print(f"   Found {len(tools)} tools:")
    for tool in tools:
        print(f"   - {tool.name}: {tool.description}")

    # Test 2: Check availability
    print("\n2️⃣ Testing check_availability...")
    result = await call_tool(
        "check_availability", {"date": "Friday", "time": "7:30 PM", "party_size": 2}
    )
    print(f"   Response: {result[0].text[:100]}...")

    # Test 3: Get menu
    print("\n3️⃣ Testing get_menu...")
    result = await call_tool("get_menu", {"query": "vegetarian options"})
    print(f"   Response: {result[0].text[:100]}...")

    # Test 4: Get hours
    print("\n4️⃣ Testing get_opening_hours...")
    result = await call_tool("get_opening_hours", {})
    print(f"   Response: {result[0].text[:100]}...")

    print("\n✅ All tests completed!")
    print("\n📝 Next steps:")
    print("   1. Add MCP server to Claude Desktop config")
    print("   2. Restart Claude Desktop")
    print("   3. Try: 'Book dinner for 2 at La Bella Vita next Friday 7:30 PM'")


if __name__ == "__main__":
    asyncio.run(main())
