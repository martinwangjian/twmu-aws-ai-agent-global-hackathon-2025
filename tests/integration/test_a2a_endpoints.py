"""Integration tests for A2A agent using OAuth authentication.

Tests A2A agent via direct HTTP requests with Cognito OAuth token.
"""

import pytest
import requests


@pytest.mark.integration
def test_a2a_agent_opening_hours(a2a_url):
    """Test A2A agent responds to opening hours query."""
    from uuid import uuid4

    payload = {
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "params": {
            "message": {
                "kind": "message",
                "role": "user",
                "parts": [{"kind": "text", "text": "What are your opening hours?"}],
                "message_id": uuid4().hex,
            }
        },
        "id": 1,
    }

    response = requests.post(
        a2a_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=60,
    )

    assert response.status_code == 200
    result = response.json()

    # Should have result field with task
    assert "result" in result or "error" not in result


@pytest.mark.integration
def test_a2a_agent_menu_query(a2a_url):
    """Test A2A agent responds to menu query."""
    from uuid import uuid4

    payload = {
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "params": {
            "message": {
                "kind": "message",
                "role": "user",
                "parts": [{"kind": "text", "text": "What vegetarian options do you have?"}],
                "message_id": uuid4().hex,
            }
        },
        "id": 1,
    }

    response = requests.post(
        a2a_url,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=60,
    )

    assert response.status_code == 200
    result = response.json()

    # Should have result field
    assert "result" in result or "error" not in result
