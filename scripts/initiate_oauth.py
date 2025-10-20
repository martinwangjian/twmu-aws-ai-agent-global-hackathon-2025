#!/usr/bin/env python3
"""Initiate OAuth flow by calling Gateway target directly.

This triggers the Gateway to return an OAuth authorization URL.
"""

import json
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
import httpx

# Load config
config = json.loads((project_root / "gateway_config.json").read_text())
calendar_id = os.environ.get("GOOGLE_CALENDAR_ID", "primary")

# Get token
client = GatewayClient(region_name=config["region"])
token = client.get_access_token_for_cognito(config["client_info"])

print("=" * 80)
print("INITIATING OAUTH FLOW")
print("=" * 80)
print(f"\nGateway: {config['gateway_url']}")
print(f"Target: {config.get('calendar_target_id', 'GoogleCalendar')}")
print(f"Calendar ID: {calendar_id}\n")

# Try to list events - this should trigger OAuth if not authorized
print("Attempting to list calendar events...")
print("(This will fail and return OAuth URL if not authorized)\n")

response = httpx.post(
    config["gateway_url"],
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "GoogleCalendar___listEvents",
            "arguments": {
                "calendarId": calendar_id,
                "maxResults": 1
            }
        }
    },
    timeout=30,
)

result = response.json()

print("=" * 80)
print("RESPONSE")
print("=" * 80)
print(json.dumps(result, indent=2))

# Check for OAuth URL in error
if "error" in result:
    error_msg = str(result["error"])
    if "oauth" in error_msg.lower() or "authorize" in error_msg.lower():
        print("\n" + "=" * 80)
        print("✅ OAUTH URL FOUND IN ERROR")
        print("=" * 80)
        print("\nLook for a URL in the error message above.")
        print("Open that URL in your browser to authorize.")
    else:
        print("\n" + "=" * 80)
        print("❌ NO OAUTH URL FOUND")
        print("=" * 80)
        print("\nThe error doesn't contain an OAuth URL.")
        print("Try the manual OAuth URL method:")
        print("\nRun: uv run python scripts/complete_oauth_flow.py")

elif "result" in result:
    if result.get("result", {}).get("isError"):
        print("\n" + "=" * 80)
        print("⚠️  ERROR RESPONSE")
        print("=" * 80)
        content = result["result"].get("content", [])
        if content:
            error_text = content[0].get("text", "")
            print(f"\nError: {error_text}")
            
            if "oauth" in error_text.lower() or "authorize" in error_text.lower():
                print("\n✅ This looks like an OAuth error.")
                print("Look for authorization URL in the error above.")
    else:
        print("\n" + "=" * 80)
        print("✅ SUCCESS - ALREADY AUTHORIZED!")
        print("=" * 80)
        print("\nOAuth is already complete. You can create bookings now.")
        print("\nTest booking:")
        print("  uv run python scripts/test_gateway_booking.py")
