#!/usr/bin/env python3
"""Setup AgentCore Gateway with OAuth authorization.

This script creates:
1. Cognito User Pool for OAuth (automatic via toolkit)
2. AgentCore Gateway with MCP protocol
3. Saves configuration to gateway_config.json

Usage:
    python scripts/setup_gateway.py
"""

import json
import logging
import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient

# Configuration
REGION = os.environ.get("AWS_REGION", "us-east-1")
GATEWAY_NAME = "restaurant-booking-gateway"
CONFIG_FILE = project_root / "gateway_config.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_gateway():
    """Create Gateway with OAuth authorization."""
    logger.info("🚀 Setting up AgentCore Gateway...")
    logger.info(f"Region: {REGION}")
    logger.info(f"Gateway name: {GATEWAY_NAME}\n")

    # Initialize client
    client = GatewayClient(region_name=REGION)
    client.logger.setLevel(logging.INFO)

    # Step 1: Create OAuth authorizer with Cognito
    logger.info("Step 1: Creating OAuth authorization server...")
    cognito_response = client.create_oauth_authorizer_with_cognito(GATEWAY_NAME)
    logger.info("✓ Authorization server created\n")

    # Step 2: Create Gateway
    logger.info("Step 2: Creating Gateway...")
    gateway = client.create_mcp_gateway(
        name=GATEWAY_NAME,
        role_arn=None,  # Auto-create role
        authorizer_config=cognito_response["authorizer_config"],
        enable_semantic_search=True,
    )
    logger.info(f"✓ Gateway created: {gateway['gatewayUrl']}\n")

    # Step 3: Fix IAM permissions
    client.fix_iam_permissions(gateway)
    logger.info("⏳ Waiting 30s for IAM propagation...")
    time.sleep(30)
    logger.info("✓ IAM permissions configured\n")

    # Step 4: Save configuration
    config = {
        "gateway_url": gateway["gatewayUrl"],
        "gateway_id": gateway["gatewayId"],
        "gateway_arn": gateway.get("gatewayArn"),
        "region": REGION,
        "client_info": cognito_response["client_info"],
    }

    CONFIG_FILE.write_text(json.dumps(config, indent=2))

    logger.info("=" * 60)
    logger.info("✅ Gateway setup complete!")
    logger.info(f"Gateway URL: {gateway['gatewayUrl']}")
    logger.info(f"Gateway ID: {gateway['gatewayId']}")
    logger.info(f"\nConfiguration saved to: {CONFIG_FILE}")
    logger.info("\nNext step: Run 'python scripts/add_calendar_target.py'")
    logger.info("=" * 60)

    return config


if __name__ == "__main__":
    try:
        setup_gateway()
    except Exception as e:
        logger.error(f"❌ Gateway setup failed: {e}")
        sys.exit(1)
