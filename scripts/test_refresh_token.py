#!/usr/bin/env python3
"""Test refresh token authentication."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env
from dotenv import load_dotenv

from mcp_server.a2a_orchestrator_mcp import get_cognito_token

load_dotenv()

try:
    token = get_cognito_token()
    print(f"✅ Successfully obtained token (length: {len(token)})")  # noqa: T201
    print(f"Token preview: {token[:50]}...")  # noqa: T201
except Exception as e:
    print(f"❌ Failed to get token: {e}")  # noqa: T201
    sys.exit(1)
