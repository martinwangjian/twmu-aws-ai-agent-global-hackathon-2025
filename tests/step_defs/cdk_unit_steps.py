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

"""BDD step definitions for CDK unit tests."""

from aws_cdk import App
from aws_cdk.assertions import Match, Template
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../features/cdk_unit.feature")


@given("a CDK app with BookingAgentStack")
def cdk_app(context):
    """Create CDK app with stack."""
    app = App()
    from cdk_infra.cdk_infra.agent_stack import BookingAgentStack

    # Use mock ARN for testing
    mock_arn = "arn:aws:bedrock-agentcore:us-east-1:123456789012:runtime/test-agent"
    stack = BookingAgentStack(app, "TestStack", agentcore_arn=mock_arn)
    context["app"] = app
    context["stack"] = stack


@when("I synthesize the stack")
def synthesize_stack(context):
    """Synthesize CDK stack to CloudFormation."""
    template = Template.from_stack(context["stack"])
    context["template"] = template


@then("synthesis should succeed")
def synthesis_succeeds(context):
    """Verify synthesis succeeded."""
    assert context["template"] is not None


@then("the template should be valid CloudFormation")
def valid_cloudformation(context):
    """Verify template is valid."""
    template = context["template"]
    # Check basic CloudFormation structure
    template_json = template.to_json()
    assert "Resources" in template_json


@then(parsers.parse("the stack should contain {count:d} Lambda function"))
def lambda_count(count, context):
    """Verify Lambda function count."""
    template = context["template"]
    template.resource_count_is("AWS::Lambda::Function", count)


@then(parsers.parse('the Lambda should have runtime "{runtime}"'))
def lambda_runtime(runtime, context):
    """Verify Lambda runtime."""
    template = context["template"]
    template.has_resource_properties("AWS::Lambda::Function", {"Runtime": runtime})


@then(parsers.parse('the Lambda should have architecture "{arch}"'))
def lambda_architecture(arch, context):
    """Verify Lambda architecture."""
    template = context["template"]
    template.has_resource_properties("AWS::Lambda::Function", {"Architectures": [arch]})


@then(parsers.parse("the Lambda should have timeout {seconds:d} seconds"))
def lambda_timeout(seconds, context):
    """Verify Lambda timeout."""
    template = context["template"]
    template.has_resource_properties("AWS::Lambda::Function", {"Timeout": seconds})


@then(parsers.parse("the Lambda should have memory {memory:d} MB"))
def lambda_memory(memory, context):
    """Verify Lambda memory."""
    template = context["template"]
    template.has_resource_properties("AWS::Lambda::Function", {"MemorySize": memory})


@then(parsers.parse('Lambda should have permission "{permission}"'))
def lambda_permission(permission, context):
    """Verify Lambda IAM permission."""
    template = context["template"]
    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Statement": Match.array_with([Match.object_like({"Action": permission})])
            }
        },
    )


@then("the permission should include runtime endpoint wildcard")
def permission_wildcard(context):
    """Verify permission includes wildcard."""
    template = context["template"]
    # Check that Resource includes wildcard pattern
    template.has_resource_properties(
        "AWS::IAM::Policy",
        {
            "PolicyDocument": {
                "Statement": Match.array_with(
                    [
                        Match.object_like(
                            {
                                "Resource": Match.array_with(
                                    [Match.string_like_regexp(".*runtime-endpoint/\\*")]
                                )
                            }
                        )
                    ]
                )
            }
        },
    )


@then(parsers.parse("the stack should contain {count:d} Lambda Function URL"))
def function_url_count(count, context):
    """Verify Function URL count."""
    template = context["template"]
    template.resource_count_is("AWS::Lambda::Url", count)


@then(parsers.parse('the Function URL should have auth type "{auth_type}"'))
def function_url_auth(auth_type, context):
    """Verify Function URL auth type."""
    template = context["template"]
    template.has_resource_properties("AWS::Lambda::Url", {"AuthType": auth_type})


@then(parsers.parse('Lambda should have environment variable "{var_name}"'))
def lambda_env_var(var_name, context):
    """Verify Lambda environment variable exists."""
    template = context["template"]
    template.has_resource_properties(
        "AWS::Lambda::Function",
        {"Environment": {"Variables": Match.object_like({var_name: Match.any_value()})}},
    )
