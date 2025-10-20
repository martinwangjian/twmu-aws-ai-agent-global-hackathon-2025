#!/usr/bin/env python3
# ruff: noqa: DTZ005
"""E2E test for WhatsApp memory integration."""

import json
import os
from datetime import datetime

import boto3
import pytest


@pytest.fixture
def agentcore_client():
    """AgentCore client fixture."""
    return boto3.client("bedrock-agentcore", region_name="us-east-1")


@pytest.fixture
def runtime_arn():
    """Get AgentCore runtime ARN."""
    arn = os.getenv("AGENTCORE_RUNTIME_ARN")
    if not arn:
        with open(".agentcore-runtime-arn") as f:
            arn = f.read().strip()
    return arn


def test_memory_within_session(agentcore_client, runtime_arn):
    """Test memory works within same session."""
    actor_id = "23012345678"
    session_id = f"test-e2e-memory-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

    # Message 1: Store information
    response1 = agentcore_client.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=session_id,
        payload=json.dumps(
            {
                "prompt": "My name is Alice and I love Italian food",
                "actor_id": actor_id,
                "session_id": session_id,
            }
        ),
    )
    result1 = json.loads(response1["response"].read())
    assert result1.get("status") == "success"
    assert "Alice" in result1.get("result", "")

    # Message 2: Recall information
    response2 = agentcore_client.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=session_id,
        payload=json.dumps(
            {
                "prompt": "What's my name and food preference?",
                "actor_id": actor_id,
                "session_id": session_id,
            }
        ),
    )
    result2 = json.loads(response2["response"].read())
    assert result2.get("status") == "success"

    # Should remember both name and food preference
    response_text = result2.get("result", "").lower()
    assert "alice" in response_text
    assert "italian" in response_text


def test_memory_isolation_by_actor(agentcore_client, runtime_arn):
    """Test memory is isolated per actor."""
    session_id = f"test-isolation-memory-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

    # Actor 1 stores info
    actor1 = "11111111111"
    response1 = agentcore_client.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=session_id,
        payload=json.dumps(
            {
                "prompt": "My name is Bob",
                "actor_id": actor1,
                "session_id": session_id,
            }
        ),
    )
    result1 = json.loads(response1["response"].read())
    assert "Bob" in result1.get("result", "")

    # Actor 2 should NOT see Actor 1's info
    actor2 = "22222222222"
    response2 = agentcore_client.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=session_id,
        payload=json.dumps(
            {
                "prompt": "What's my name?",
                "actor_id": actor2,
                "session_id": session_id,
            }
        ),
    )
    result2 = json.loads(response2["response"].read())

    # Should NOT know Bob's name
    response_text = result2.get("result", "").lower()
    assert "bob" not in response_text
    assert "don't have" in response_text or "don't know" in response_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
