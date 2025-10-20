#!/usr/bin/env python3
"""Test Gateway booking directly to see actual errors."""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient

# Load config
config = json.loads((project_root / "gateway_config.json").read_text())
calendar_id = os.environ.get("GOOGLE_CALENDAR_ID", "primary")

# Get token
client = GatewayClient(region_name=config["region"])
token = client.get_access_token_for_cognito(config["client_info"])

print(f"Gateway URL: {config['gateway_url']}")
print(f"Calendar ID: {calendar_id}")
print(f"Token: {token[:50]}...\n")

# Test: List tools
print("=" * 80)
print("TEST 1: List available tools")
print("=" * 80)

import httpx

response = httpx.post(
    config["gateway_url"],
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
    timeout=30,
)

print(f"Status: {response.status_code}")
result = response.json()
if "result" in result and "tools" in result["result"]:
    tools = result["result"]["tools"]
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool['name']}")
else:
    print(f"Response: {json.dumps(result, indent=2)}")

# Test: Create event
print("\n" + "=" * 80)
print("TEST 2: Create calendar event")
print("=" * 80)

start_time = datetime(2025, 1, 10, 19, 0, 0)  # Jan 10, 2025 7pm
end_time = start_time + timedelta(hours=2)

event_data = {
    "calendarId": calendar_id,
    "summary": "Restaurant Booking - John Doe (2 guests)",
    "description": "Customer: John Doe\nPhone: +23055030467\nParty size: 2",
    "start": {"dateTime": start_time.isoformat() + "+04:00", "timeZone": "Indian/Mauritius"},
    "end": {"dateTime": end_time.isoformat() + "+04:00", "timeZone": "Indian/Mauritius"},
}

print(f"Event data: {json.dumps(event_data, indent=2)}\n")

response = httpx.post(
    config["gateway_url"],
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": "GoogleCalendarLambda___createEvent", "arguments": event_data},
    },
    timeout=30,
)

print(f"Status: {response.status_code}")
result = response.json()
print(f"Response: {json.dumps(result, indent=2)}")

if "error" in result:
    print(f"\n❌ ERROR: {result['error']}")
elif "result" in result:
    print(f"\n✅ SUCCESS!")
    if isinstance(result["result"], list) and len(result["result"]) > 0:
        content = result["result"][0].get("content", [])
        if content:
            print(f"Event created: {content[0].get('text', 'No details')}")
