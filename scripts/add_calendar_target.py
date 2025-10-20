#!/usr/bin/env python3
"""Add Google Calendar target to AgentCore Gateway.

Prerequisites:
1. Run setup_gateway.py first
2. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env

Usage:
    python scripts/add_calendar_target.py
"""

import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient

# Configuration
REGION = os.environ.get("AWS_REGION", "us-east-1")
CONFIG_FILE = project_root / "gateway_config.json"
OPENAPI_FILE = project_root / "config" / "google_calendar_openapi.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_calendar_target():
    """Add Google Calendar as Gateway target."""
    # Load Gateway config
    if not CONFIG_FILE.exists():
        logger.error("❌ gateway_config.json not found!")
        logger.error("Please run 'python scripts/setup_gateway.py' first")
        sys.exit(1)

    config = json.loads(CONFIG_FILE.read_text())
    logger.info(f"📋 Loaded Gateway config: {config['gateway_id']}")

    # Load OpenAPI spec
    if not OPENAPI_FILE.exists():
        logger.error(f"❌ OpenAPI spec not found: {OPENAPI_FILE}")
        sys.exit(1)

    calendar_spec = json.loads(OPENAPI_FILE.read_text())
    logger.info(f"📋 Loaded OpenAPI spec: {calendar_spec['info']['title']}")

    # Get Google OAuth credentials
    google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
    google_client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

    if not google_client_id or not google_client_secret:
        logger.error("❌ Missing Google OAuth credentials!")
        logger.error("Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env")
        sys.exit(1)

    # Initialize client
    client = GatewayClient(region_name=REGION)
    gateway = client.client.get_gateway(gatewayIdentifier=config["gateway_id"])

    logger.info("\n🔧 Adding Google Calendar target...")

    # Add target with OAuth
    target = client.create_mcp_gateway_target(
        gateway=gateway,
        name="GoogleCalendar",
        target_type="openApiSchema",
        target_payload={"inlinePayload": json.dumps(calendar_spec)},
        credentials={
            "oauth2_provider_config": {
                "customOauth2ProviderConfig": {
                    "oauthDiscovery": {
                        "authorizationServerMetadata": {
                            "issuer": "https://accounts.google.com",
                            "authorizationEndpoint": "https://accounts.google.com/o/oauth2/v2/auth",
                            "tokenEndpoint": "https://oauth2.googleapis.com/token",
                        }
                    },
                    "clientId": google_client_id,
                    "clientSecret": google_client_secret,
                }
            }
        },
    )

    # Update config with target info
    config["calendar_target_id"] = target["targetId"]
    CONFIG_FILE.write_text(json.dumps(config, indent=2))

    logger.info("=" * 60)
    logger.info("✅ Google Calendar target added!")
    logger.info(f"Target ID: {target['targetId']}")
    logger.info(f"\nAvailable tools:")
    logger.info("  - listEvents: List calendar events")
    logger.info("  - createEvent: Create booking event")
    logger.info("  - deleteEvent: Cancel booking")
    logger.info("\nNext step: Update agent to use Gateway tools")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        add_calendar_target()
    except Exception as e:
        logger.error(f"❌ Failed to add target: {e}")
        sys.exit(1)
