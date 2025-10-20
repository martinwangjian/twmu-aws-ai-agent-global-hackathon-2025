#!/usr/bin/env python3
"""Cleanup AgentCore Gateway and associated resources.

This script deletes:
1. Gateway targets
2. Gateway
3. Cognito User Pool (OAuth)

Usage:
    python scripts/cleanup_gateway.py
"""

import json
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient

# Configuration
CONFIG_FILE = project_root / "gateway_config.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup_gateway():
    """Delete Gateway and associated resources."""
    # Load config
    if not CONFIG_FILE.exists():
        logger.warning("⚠️  gateway_config.json not found - nothing to cleanup")
        return

    config = json.loads(CONFIG_FILE.read_text())
    logger.info(f"📋 Loaded Gateway config: {config['gateway_id']}")

    # Initialize client
    client = GatewayClient(region_name=config["region"])

    logger.info("\n🗑️  Cleaning up Gateway resources...")

    # Cleanup Gateway (also deletes targets)
    try:
        client.cleanup_gateway(config["gateway_id"], config["client_info"])
        logger.info("✓ Gateway and targets deleted")
    except Exception as e:
        logger.error(f"❌ Failed to delete Gateway: {e}")

    # Remove config file
    CONFIG_FILE.unlink()
    logger.info("✓ Removed gateway_config.json")

    logger.info("\n✅ Cleanup complete!")


if __name__ == "__main__":
    try:
        cleanup_gateway()
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        sys.exit(1)
