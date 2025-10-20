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

#!/usr/bin/env python3
"""CDK app entry point."""

import os
from pathlib import Path

import aws_cdk as cdk
from dotenv import load_dotenv

from cdk_infra.calendar_service_stack import CalendarServiceStack
from cdk_infra.cognito_stack import CognitoStack
from cdk_infra.config_stack import ConfigStack
from cdk_infra.knowledge_base_stack import RestaurantKBStack
from cdk_infra.payment_bucket_stack import PaymentBucketStack
from cdk_infra.whatsapp_stack import WhatsAppStack

# Load .env file for AWS credentials and VPC config
env_file = Path(__file__).parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

app = cdk.App()

# Get AgentCore ARN from file or environment
agentcore_arn = os.getenv("AGENTCORE_RUNTIME_ARN")
if not agentcore_arn:
    arn_file = Path(__file__).parent.parent / ".agentcore-runtime-arn"
    if arn_file.exists():
        agentcore_arn = arn_file.read_text().strip()
    else:
        raise ValueError(
            "AgentCore ARN not found. Run: ./scripts/deploy.sh or set AGENTCORE_RUNTIME_ARN"
        )

# Get memory ARN from environment
memory_arn = os.getenv("AGENTCORE_MEMORY_ARN")

# Get WhatsApp Business Account ID from environment (optional)
whatsapp_business_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")

# Deploy Cognito stack for A2A authentication
CognitoStack(
    app,
    "CognitoStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region="us-east-1",
    ),
)

# Deploy Config stack for runtime parameters
ConfigStack(
    app,
    "ConfigStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region="us-east-1",
    ),
)

# Deploy Payment Bucket stack for AP2 payment tracking
PaymentBucketStack(
    app,
    "PaymentBucketStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region="us-east-1",
    ),
)

# Deploy WhatsApp stack
WhatsAppStack(
    app,
    "WhatsAppStack",
    agentcore_runtime_arn=agentcore_arn,
    agentcore_memory_arn=memory_arn,
    whatsapp_business_account_id=whatsapp_business_id,
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region="us-east-1",
    ),
)

# Deploy Knowledge Base stack
RestaurantKBStack(
    app,
    "RestaurantKBStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region="us-east-1",
    ),
)

# Deploy Calendar Service stack
calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
CalendarServiceStack(
    app,
    "CalendarServiceStack",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region="us-east-1",
    ),
)

app.synth()
