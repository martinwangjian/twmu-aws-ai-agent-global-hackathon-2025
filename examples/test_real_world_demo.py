"""Test script for real-world A2A booking demo

Simulates the full booking flow to verify all components work.
"""

import asyncio
from datetime import datetime

import httpx

AGENT_URL = "https://restaurant-booking-agent.teamwork-mu.net"


async def test_agent_discovery():
    """Phase 1: Discover the restaurant agent"""
    print("🔍 Phase 1: Agent Discovery")
    print("-" * 50)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AGENT_URL}/.well-known/agent-card.json")
        card = response.json()

        print(f"✅ Found: {card['name']}")
        print(f"   Protocol: A2A v{card['protocolVersion']}")
        print(f"   Skills: {len(card['skills'])}")
        print(f"   URL: {card['url']}")
        print()

        return card


async def test_information_query():
    """Phase 2: Query restaurant information"""
    print("📋 Phase 2: Information Gathering")
    print("-" * 50)

    message = {
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {
            "message": {
                "kind": "message",
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": "Tell me about your restaurant. Do you have vegetarian options?",
                    }
                ],
                "message_id": f"test_{datetime.now().timestamp()}",
            }
        },
        "id": 1,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{AGENT_URL}/", json=message)
        data = response.json()

        if "error" in data and data["error"]:
            print(f"❌ Error: {data['error']}")
            return None

        result = data.get("result", {})
        print("✅ Response received")
        print(f"   Type: {result.get('kind', 'unknown')}")
        print()

        return result


async def test_availability_check():
    """Phase 3: Check availability"""
    print("📅 Phase 3: Availability Check")
    print("-" * 50)

    message = {
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {
            "message": {
                "kind": "message",
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": "Check availability for 2 people next Friday at 7:30 PM",
                    }
                ],
                "message_id": f"test_{datetime.now().timestamp()}",
            }
        },
        "id": 2,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(f"{AGENT_URL}/", json=message)
        data = response.json()

        if "error" in data and data["error"]:
            print(f"❌ Error: {data['error']}")
            return None

        result = data.get("result", {})
        print("✅ Availability check completed")
        print(f"   Type: {result.get('kind', 'unknown')}")
        print()

        return result


async def main():
    """Run full demo test"""
    print("=" * 50)
    print("Real-World A2A Booking Demo Test")
    print("=" * 50)
    print()

    try:
        # Phase 1: Discovery
        card = await test_agent_discovery()
        if not card:
            print("❌ Agent discovery failed")
            return

        # Phase 2: Information
        info = await test_information_query()
        if not info:
            print("⚠️  Information query had issues")

        # Phase 3: Availability
        availability = await test_availability_check()
        if not availability:
            print("⚠️  Availability check had issues")

        print("=" * 50)
        print("✅ Demo test completed!")
        print("=" * 50)
        print()
        print("Next steps:")
        print("1. Open Claude Desktop")
        print("2. Use the demo script from REAL_WORLD_DEMO.md")
        print("3. Experience the full booking flow")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
