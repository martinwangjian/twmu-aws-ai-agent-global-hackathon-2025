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

"""BDD step definitions for Lambda E2E tests."""

import json
import time

import boto3
import requests
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/lambda_e2e.feature")

STACK_NAME = "BookingAgentStack"


@given("the infrastructure is deployed")
def infrastructure_deployed(context):
    """Verify infrastructure is deployed."""
    cfn = boto3.client("cloudformation")
    response = cfn.describe_stacks(StackName=STACK_NAME)
    assert len(response["Stacks"]) == 1
    context["stack"] = response["Stacks"][0]


@given("the Function URL is available")
def function_url_available(context):
    """Get Function URL from stack outputs."""
    stack = context["stack"]
    outputs = {o["OutputKey"]: o["OutputValue"] for o in stack["Outputs"]}
    context["function_url"] = outputs["InvokerURL"]


@when(parsers.parse('I POST to Function URL with prompt "{prompt}"'))
def post_to_function_url(prompt, context):
    """POST request to Function URL."""
    start_time = time.time()
    response = requests.post(
        context["function_url"],
        json={"prompt": prompt},
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    end_time = time.time()

    context["response"] = response
    context["response_time"] = end_time - start_time


@when("I POST to Function URL with invalid JSON")
def post_invalid_json(context):
    """POST invalid JSON to Function URL."""
    response = requests.post(
        context["function_url"],
        data="invalid json",
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    context["response"] = response


@then(parsers.parse("the HTTP status should be {status:d}"))
def http_status(status, context):
    """Verify HTTP status code."""
    assert context["response"].status_code == status


@then("the response should be valid JSON")
def valid_json(context):
    """Verify response is valid JSON."""
    try:
        context["response"].json()
    except json.JSONDecodeError as e:
        raise AssertionError("Response is not valid JSON") from e


@then(parsers.parse("the response time should be less than {seconds:d} seconds"))
def response_time_check(seconds, context):
    """Verify response time."""
    assert context["response_time"] < seconds
