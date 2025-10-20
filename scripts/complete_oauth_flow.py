#!/usr/bin/env python3
"""Helper script to complete Google Calendar OAuth flow.

This script provides instructions for completing OAuth via AWS Console,
which is the most reliable method.
"""

import json
from pathlib import Path

# Load Gateway config
config_path = Path(__file__).parent.parent / "gateway_config.json"
if not config_path.exists():
    print("❌ gateway_config.json not found!")
    print("Run 'python scripts/setup_gateway.py' first")
    exit(1)

config = json.load(config_path.open())

print("\n" + "=" * 80)
print("GOOGLE CALENDAR OAUTH SETUP")
print("=" * 80)

print("\n📋 Your Gateway Details:")
print(f"  Gateway ID: {config['gateway_id']}")
print(f"  Gateway URL: {config['gateway_url']}")
print(f"  Region: {config['region']}")

print("\n" + "=" * 80)
print("METHOD 1: AWS Console (RECOMMENDED)")
print("=" * 80)

print("""
This is the most reliable way to complete OAuth:

1. Open AWS Console:
   https://console.aws.amazon.com/bedrock-agentcore/

2. Click "Gateways" in left sidebar

3. Click your gateway: {gateway_id}

4. Click "Targets" tab

5. Click target: "GoogleCalendar"

6. Under "Outbound authentication", click "Test connection"

7. A popup will open with Google OAuth flow

8. Sign in with your Google account (calendar owner)

9. Click "Allow" to authorize access

10. Close popup when authorization completes

11. Run test script to verify:
    uv run python scripts/test_gateway_booking.py
""".format(gateway_id=config['gateway_id']))

print("\n" + "=" * 80)
print("METHOD 2: Direct OAuth URL (ALTERNATIVE)")
print("=" * 80)

# Generate OAuth URL
import os
client_id = os.environ.get('GOOGLE_CLIENT_ID', 'YOUR_CLIENT_ID')
gateway_id = config['gateway_id']

auth_url = (
    f"https://accounts.google.com/o/oauth2/v2/auth"
    f"?client_id={client_id}"
    f"&redirect_uri=https://{gateway_id}.gateway.bedrock-agentcore.us-east-1.amazonaws.com/oauth2callback"
    f"&response_type=code"
    f"&scope=https://www.googleapis.com/auth/calendar"
    f"&access_type=offline"
    f"&prompt=consent"
    f"&state=gateway-oauth"
)

print(f"""
If AWS Console method doesn't work, try this:

1. Open this URL in your browser:
   {auth_url}

2. Sign in and authorize

3. You'll see "UnknownOperationException" - IGNORE IT

4. Wait 30 seconds for Gateway to process

5. Run test script:
   uv run python scripts/test_gateway_booking.py

Note: This method is less reliable. Use AWS Console if possible.
""")

print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

print("""
After completing OAuth, verify it works:

1. Run test script:
   export $(cat .env | grep -v '^#' | xargs)
   uv run python scripts/test_gateway_booking.py

2. Expected output:
   ✅ SUCCESS!
   Event created: {...}

3. Check Google Calendar:
   https://calendar.google.com/
   Look for test event on January 10, 2025

If you see "InternalServerException", OAuth didn't complete.
Try AWS Console method again.
""")

print("=" * 80)
