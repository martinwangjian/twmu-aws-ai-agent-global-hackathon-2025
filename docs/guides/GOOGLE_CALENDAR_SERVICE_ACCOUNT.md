# Google Calendar Service Account Setup (Alternative to OAuth)

**Purpose**: Simpler authentication method for testing. No OAuth flow needed.

## Why Service Account?

**OAuth issues**:

- ❌ Gateway OAuth callback not working reliably (preview limitation)
- ❌ Manual authorization flow complex
- ❌ Token refresh issues

**Service Account benefits**:

- ✅ No OAuth flow needed
- ✅ Works immediately after setup
- ✅ No token expiration issues
- ✅ Perfect for testing

## Setup Steps (5 minutes)

### Step 1: Create Service Account

1. Go to [Google Cloud Console - Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Select your project: `restaurant-booking-bot`
3. Click **+ Create Service Account**
4. Fill in:
   - **Service account name**: `restaurant-booking-agent`
   - **Service account ID**: (auto-filled)
   - **Description**: `Service account for restaurant booking calendar`
5. Click **Create and Continue**
6. Skip "Grant this service account access" (click **Continue**)
7. Skip "Grant users access" (click **Done**)

### Step 2: Create Key

1. Find your new service account in the list
2. Click the **⋮** (three dots) → **Manage keys**
3. Click **Add Key** → **Create new key**
4. Select **JSON**
5. Click **Create**
6. Save the downloaded JSON file as `service-account-key.json` in your project root

**File looks like**:

```json
{
  "type": "service_account",
  "project_id": "restaurant-booking-bot-123456",
  "private_key_id": "abc123...",
  "private_key": "[REDACTED - Use actual service account key]",
  "client_email": "restaurant-booking-agent@restaurant-booking-bot-123456.iam.gserviceaccount.com",
  "client_id": "123456789",
  ...
}
```

### Step 3: Share Calendar with Service Account

1. Go to [Google Calendar](https://calendar.google.com/)
2. Find your calendar: "La Bella Vita Bookings"
3. Click **⋮** (three dots) → **Settings and sharing**
4. Scroll to **Share with specific people**
5. Click **+ Add people**
6. Enter the service account email from the JSON file:
   ```
   restaurant-booking-agent@restaurant-booking-bot-123456.iam.gserviceaccount.com
   ```
7. Set permission: **Make changes to events**
8. Click **Send**

### Step 4: Update Gateway Target

Now we need to recreate the Gateway target to use Service Account instead of OAuth.

**Option A: Recreate target with script**:

Create `scripts/add_calendar_target_service_account.py`:

```python
#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient

# Load configs
config = json.loads((project_root / "gateway_config.json").read_text())
service_account = json.loads((project_root / "service-account-key.json").read_text())
calendar_spec = json.loads((project_root / "config" / "google_calendar_openapi.json").read_text())

client = GatewayClient(region_name=config["region"])
gateway = client.client.get_gateway(gatewayIdentifier=config["gateway_id"])

# Delete old target
if "calendar_target_id" in config:
    print(f"Deleting old target: {config['calendar_target_id']}")
    try:
        client.client.delete_gateway_target(
            gatewayIdentifier=config["gateway_id"],
            targetId=config["calendar_target_id"]
        )
        print("✓ Old target deleted")
    except:
        print("⚠️  Could not delete old target (may not exist)")

# Create new target with service account
print("\nCreating new target with Service Account...")

# For service account, we use API key authentication with the private key
target = client.create_mcp_gateway_target(
    gateway=gateway,
    name="GoogleCalendarServiceAccount",
    target_type="openApiSchema",
    target_payload={"inlinePayload": json.dumps(calendar_spec)},
    credentials={
        "api_key": service_account["private_key"],
        "credential_location": "HEADER",
        "credential_parameter_name": "Authorization"
    }
)

config["calendar_target_id"] = target["targetId"]
(project_root / "gateway_config.json").write_text(json.dumps(config, indent=2))

print(f"✅ Service Account target created: {target['targetId']}")
print("\nTest booking:")
print("  uv run python scripts/test_gateway_booking.py")
```

Run:

```bash
uv run python scripts/add_calendar_target_service_account.py
```

**Option B: Manual via AWS Console** (if script doesn't work):

Unfortunately, AgentCore Gateway doesn't support Service Account authentication directly. We need to use OAuth.

## Alternative: Fix OAuth Flow

Since Service Account isn't directly supported by Gateway, let's try one more OAuth approach:

### Use Google Cloud Console to Generate Refresh Token

1. Install gcloud CLI: https://cloud.google.com/sdk/docs/install
2. Run:
   ```bash
   gcloud auth application-default login --scopes=https://www.googleapis.com/auth/calendar
   ```
3. This creates `~/.config/gcloud/application_default_credentials.json`
4. Extract the `refresh_token` from that file
5. Manually add it to Gateway's credential provider (requires AWS CLI/SDK)

This is complex. **Recommendation**: Wait for AgentCore Gateway OAuth to be fixed in a future release, or use a different approach.

## Recommended: Skip Calendar for Now

For the hackathon demo, you can:

1. **Mock the booking**: Agent confirms booking but doesn't create calendar event
2. **Manual calendar**: Create events manually after agent confirms
3. **Alternative**: Use a simpler API (like Airtable or Google Sheets) that has better OAuth support

Would you like me to implement a mock booking system for the demo?
