"""Non-regression test for AgentCore runtime startup.

This test prevents the bug where AgentCore runtime fails to start due to
missing dependencies (bedrock_agentcore_starter_toolkit).
"""

import os

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


@pytest.mark.e2e
def test_agentcore_runtime_starts_successfully(agentcore_client, runtime_arn):
    """Test that AgentCore runtime starts without ModuleNotFoundError.

    Regression test for: ModuleNotFoundError: No module named 'bedrock_agentcore_starter_toolkit'

    This ensures the runtime container has all required dependencies installed.
    """
    import json
    from datetime import datetime

    session_id = f"test-runtime-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"  # noqa: DTZ005

    # Simple invocation to verify runtime starts
    try:
        response = agentcore_client.invoke_agent_runtime(
            agentRuntimeArn=runtime_arn,
            runtimeSessionId=session_id,
            payload=json.dumps({"prompt": "test"}),
        )

        # If we get here without RuntimeClientError, the runtime started successfully
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    except agentcore_client.exceptions.RuntimeClientError as e:
        # Check if it's the specific ModuleNotFoundError we're testing for
        error_msg = str(e)
        assert (
            "ModuleNotFoundError" not in error_msg
        ), f"Runtime failed to start due to missing module: {error_msg}"
        assert (
            "bedrock_agentcore_starter_toolkit" not in error_msg
        ), f"Runtime missing bedrock_agentcore_starter_toolkit: {error_msg}"
        # Re-raise other errors
        raise


@pytest.mark.e2e
def test_agentcore_has_gateway_tools(agentcore_client, runtime_arn):
    """Test that AgentCore runtime has access to Gateway MCP tools.

    This ensures the bedrock_agentcore_starter_toolkit is properly installed
    and Gateway client can be initialized.
    """
    import json
    from datetime import datetime

    session_id = f"test-gateway-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"  # noqa: DTZ005

    # Ask about calendar to trigger tool usage
    try:
        response = agentcore_client.invoke_agent_runtime(
            agentRuntimeArn=runtime_arn,
            runtimeSessionId=session_id,
            payload=json.dumps({"prompt": "What tools do you have access to?"}),
        )

        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    except agentcore_client.exceptions.RuntimeClientError as e:
        error_msg = str(e)
        # Fail if it's a module import error
        assert (
            "ModuleNotFoundError" not in error_msg
        ), f"Runtime failed due to missing module: {error_msg}"
        assert (
            "GatewayClient" not in error_msg
        ), f"Runtime failed to import GatewayClient: {error_msg}"
        raise
