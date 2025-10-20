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

"""BDD step definitions for CDK integration tests."""

import boto3
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/cdk_integration.feature")

STACK_NAME = "BookingAgentStack"


@given("the CDK stack is deployed")
def stack_deployed(context):
    """Verify stack is deployed."""
    cfn = boto3.client("cloudformation")
    response = cfn.describe_stacks(StackName=STACK_NAME)
    assert len(response["Stacks"]) == 1
    context["stack"] = response["Stacks"][0]


@when("I deploy the CDK stack")
def deploy_stack(context):
    """Deploy CDK stack (assumes already deployed)."""
    # In real scenario, would run: cdk deploy
    # For tests, we assume stack is already deployed
    cfn = boto3.client("cloudformation")
    response = cfn.describe_stacks(StackName=STACK_NAME)
    context["stack"] = response["Stacks"][0]


@then(parsers.parse('the stack should be in "{status}" or "{alt_status}" status'))
def stack_status(status, alt_status, context):
    """Verify stack status."""
    stack = context["stack"]
    assert stack["StackStatus"] in [status, alt_status]


@then("the stack should have outputs")
def stack_has_outputs(context):
    """Verify stack has outputs."""
    stack = context["stack"]
    assert "Outputs" in stack
    assert len(stack["Outputs"]) > 0


@then("Lambda function should exist in AWS")
def lambda_exists(context):
    """Verify Lambda exists."""
    stack = context["stack"]
    # Get Lambda function name from outputs
    outputs = {o["OutputKey"]: o["OutputValue"] for o in stack["Outputs"]}
    function_name = outputs["LambdaFunctionName"]

    lambda_client = boto3.client("lambda")
    response = lambda_client.get_function(FunctionName=function_name)
    context["lambda_config"] = response["Configuration"]


@then(parsers.parse('Lambda should have tag "{tag_key}"'))
def lambda_has_tag(tag_key, context):
    """Verify Lambda has tag."""
    lambda_config = context["lambda_config"]
    lambda_client = boto3.client("lambda")
    tags = lambda_client.list_tags(Resource=lambda_config["FunctionArn"])
    assert tag_key in tags["Tags"]


@then(parsers.parse('Lambda runtime should be "{runtime}"'))
def lambda_runtime_check(runtime, context):
    """Verify Lambda runtime."""
    lambda_config = context["lambda_config"]
    assert lambda_config["Runtime"] == runtime


@then(parsers.parse('Lambda architecture should be "{arch}"'))
def lambda_arch_check(arch, context):
    """Verify Lambda architecture."""
    lambda_config = context["lambda_config"]
    assert arch in lambda_config["Architectures"]


@then(parsers.parse("Lambda timeout should be {seconds:d} seconds"))
def lambda_timeout_check(seconds, context):
    """Verify Lambda timeout."""
    lambda_config = context["lambda_config"]
    assert lambda_config["Timeout"] == seconds


@then(parsers.parse("Lambda memory should be {memory:d} MB"))
def lambda_memory_check(memory, context):
    """Verify Lambda memory."""
    lambda_config = context["lambda_config"]
    assert lambda_config["MemorySize"] == memory


@then(parsers.parse('the ARN should start with "{prefix}"'))
def arn_prefix_check(prefix, context):
    """Verify ARN prefix."""
    lambda_config = context["lambda_config"]
    env_vars = lambda_config["Environment"]["Variables"]
    arn = env_vars["AGENTCORE_RUNTIME_ARN"]
    assert arn.startswith(prefix)


@then("Function URL should be in stack outputs")
def function_url_in_outputs(context):
    """Verify Function URL in outputs."""
    stack = context["stack"]
    outputs = {o["OutputKey"]: o["OutputValue"] for o in stack["Outputs"]}
    assert "InvokerURL" in outputs
    context["function_url"] = outputs["InvokerURL"]


@then("Function URL should be accessible via HTTPS")
def function_url_https(context):
    """Verify Function URL uses HTTPS."""
    function_url = context["function_url"]
    assert function_url.startswith("https://")
