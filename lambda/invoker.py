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

"""Lambda function to invoke AgentCore runtime."""

import json
import os

import boto3

agentcore = boto3.client("bedrock-agentcore")


def handler(event, context):
    """Invoke AgentCore runtime.

    Args:
        event: Lambda event with 'prompt' in body
        context: Lambda context

    Returns:
        Response from AgentCore
    """
    runtime_arn = os.environ["AGENTCORE_RUNTIME_ARN"]

    # Parse request
    body = json.loads(event.get("body", "{}"))
    prompt = body.get("prompt", "Hello")

    # Invoke AgentCore
    response = agentcore.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=context.aws_request_id,
        payload=json.dumps({"prompt": prompt}),
    )

    # Parse response
    result = json.loads(response["response"].read())

    return {"statusCode": 200, "body": json.dumps(result)}
