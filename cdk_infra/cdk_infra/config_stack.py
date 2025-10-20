"""Configuration Stack for runtime parameters."""

import os

from aws_cdk import Stack
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class ConfigStack(Stack):
    """Store runtime configuration in SSM Parameter Store."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Bedrock model ID
        model_id = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0")
        ssm.StringParameter(
            self,
            "ModelIdParam",
            parameter_name="/restaurant-booking/model-id",
            string_value=model_id,
            description="Bedrock model ID for agent",
        )
