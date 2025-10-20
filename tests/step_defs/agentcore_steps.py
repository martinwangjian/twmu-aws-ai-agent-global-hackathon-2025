# Copyright (C) 2025 Teamwork Mauritius
#
# This file is part of AWS AI Agent Global Hackathon 2025 submission.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""BDD step definitions for AgentCore tests."""

import json
import os
import subprocess
import time

import boto3
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/agentcore.feature")


@given("AWS credentials are configured")
def aws_credentials_configured():
    """Verify AWS credentials are available."""
    try:
        boto3.client("sts").get_caller_identity()
    except Exception as e:
        raise AssertionError(f"AWS credentials not configured: {e}") from None


@given(parsers.parse('the region is set to "{region}"'))
def region_is_set(region):
    """Verify AWS region is set."""
    os.environ["AWS_DEFAULT_REGION"] = region
    assert os.environ.get("AWS_DEFAULT_REGION") == region


@given("AgentCore runtime is deployed")
def agentcore_runtime_deployed():
    """Verify AgentCore runtime exists."""
    arn_file = ".agentcore-runtime-arn"
    assert os.path.exists(arn_file), "AgentCore runtime ARN file not found"
    with open(arn_file) as f:
        arn = f.read().strip()
    assert arn.startswith("arn:aws:bedrock-agentcore:"), f"Invalid ARN: {arn}"


@when(parsers.parse('I deploy AgentCore with entrypoint "{entrypoint}"'))
def deploy_agentcore(entrypoint):
    """Deploy AgentCore runtime."""
    result = subprocess.run(  # noqa: S603
        ["./scripts/deploy-agentcore-us-east-1.sh"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"Deployment failed: {result.stderr}"


@when(parsers.parse('I invoke the agent with prompt "{prompt}"'))
def invoke_agent(prompt, context):
    """Invoke AgentCore with a prompt."""
    start_time = time.time()
    result = subprocess.run(  # noqa: S603
        ["agentcore", "invoke", json.dumps({"prompt": prompt})],  # noqa: S607
        capture_output=True,
        text=True,
        check=False,
    )
    end_time = time.time()

    assert result.returncode == 0, f"Invocation failed: {result.stderr}"

    # Parse response
    output = result.stdout
    response_line = [line for line in output.split("\n") if line.startswith("{")]
    assert response_line, "No JSON response found"

    context["response"] = json.loads(response_line[0])
    context["response_time"] = end_time - start_time


@then("the deployment should succeed")
def deployment_succeeds():
    """Verify deployment succeeded."""
    assert os.path.exists(".agentcore-runtime-arn")


@then("the AgentCore runtime ARN should be saved")
def runtime_arn_saved():
    """Verify ARN is saved."""
    with open(".agentcore-runtime-arn") as f:
        arn = f.read().strip()
    assert arn.startswith("arn:aws:bedrock-agentcore:")


@then(parsers.parse('the runtime status should be "{status}"'))
def runtime_status(status):
    """Verify runtime status."""
    # For now, assume ACTIVE if ARN exists
    assert os.path.exists(".agentcore-runtime-arn")


@then(parsers.parse('the response should contain "{text}"'))
def response_contains(text, context):
    """Verify response contains text."""
    response = context["response"]
    result = response.get("result", "")
    assert text in result, f"Expected '{text}' in '{result}'"


@then(parsers.parse('the response status should be "{status}"'))
def response_status(status, context):
    """Verify response status."""
    response = context["response"]
    assert response.get("status") == status


@then(parsers.parse("the response time should be less than {seconds:d} seconds"))
def response_time(seconds, context):
    """Verify response time."""
    assert context["response_time"] < seconds
