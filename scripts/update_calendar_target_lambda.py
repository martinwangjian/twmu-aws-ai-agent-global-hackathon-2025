#!/usr/bin/env python3
"""Update Gateway to use Calendar Lambda with checkAvailability tool."""

import json
import logging
import sys
from pathlib import Path

from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient

# Configuration
REGION = "us-east-1"
CONFIG_FILE = Path(__file__).parent.parent / "gateway_config.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def update_calendar_target():
    """Update Gateway target to use Lambda with new tools."""
    # Load Gateway config
    if not CONFIG_FILE.exists():
        logger.error("❌ gateway_config.json not found!")
        sys.exit(1)

    config = json.loads(CONFIG_FILE.read_text())
    logger.info(f"📋 Gateway: {config['gateway_id']}")
    logger.info(f"📋 Calendar Lambda: {config['calendar_lambda_arn']}")

    # Initialize client
    client = GatewayClient(region_name=REGION)
    gateway = client.client.get_gateway(gatewayIdentifier=config["gateway_id"])

    # Delete old target if exists
    if "calendar_target_id" in config:
        try:
            logger.info(f"🗑️  Deleting old target: {config['calendar_target_id']}")
            client.client.delete_gateway_target(
                gatewayIdentifier=config["gateway_id"],
                targetId=config["calendar_target_id"],
            )
        except Exception as e:
            logger.warning(f"Could not delete old target: {e}")

    logger.info("\n🔧 Creating Lambda target...")

    # Create Lambda target - toolkit will handle the schema correctly
    target = client.create_mcp_gateway_target(
        gateway=gateway,
        name="CalendarService",
        target_type="lambda",
        target_payload={"lambdaArn": config["calendar_lambda_arn"]},
    )

    # Update config
    config["calendar_target_id"] = target["targetId"]
    CONFIG_FILE.write_text(json.dumps(config, indent=2))

    logger.info("=" * 60)
    logger.info("✅ Calendar Lambda target updated!")
    logger.info(f"Target ID: {target['targetId']}")
    logger.info("\nℹ️  Note: The Lambda handler already has checkAvailability")
    logger.info("   and getAvailableSlots implemented.")
    logger.info("\nRedeploy agent to use updated system prompt:")
    logger.info("  uv run agentcore launch")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        update_calendar_target()
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
