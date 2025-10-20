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

"""CDK Stack for WhatsApp integration."""

from aws_cdk import CfnOutput, CustomResource, Duration, Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_secretsmanager as secretsmanager
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as subscriptions
from aws_cdk.custom_resources import Provider
from constructs import Construct


class WhatsAppStack(Stack):
    """WhatsApp integration stack."""

    def __init__(
        self,
        scope: Construct,
        id: str,
        agentcore_runtime_arn: str,
        agentcore_memory_arn: str | None = None,
        whatsapp_business_account_id: str | None = None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        # Reference existing S3 bucket for AgentCore session storage
        session_bucket = s3.Bucket.from_bucket_name(
            self,
            "SessionBucket",
            bucket_name=f"agentcore-sessions-{self.account}",
        )

        # SNS Topic for WhatsApp events
        whatsapp_topic = sns.Topic(
            self,
            "WhatsAppTopic",
            display_name="WhatsApp Messages",
            topic_name="WhatsAppMessages",
        )

        # Secrets Manager for WhatsApp credentials
        whatsapp_secret = secretsmanager.Secret(
            self,
            "WhatsAppSecret",
            description="WhatsApp Business API credentials",
            secret_name="whatsapp-booking/credentials",  # noqa: S106
        )

        # Lambda Orchestrator environment variables
        env_vars = {
            "AGENTCORE_RUNTIME_ARN": agentcore_runtime_arn,
            "WHATSAPP_SECRET_ARN": whatsapp_secret.secret_arn,
            "LOG_LEVEL": "INFO",
        }

        # Add memory ARN if provided
        if agentcore_memory_arn:
            env_vars["AGENTCORE_MEMORY_ARN"] = agentcore_memory_arn
        if whatsapp_business_account_id:
            env_vars["WHATSAPP_BUSINESS_ACCOUNT_ID"] = whatsapp_business_account_id

        # Use pre-built package if exists, otherwise use bundling
        from pathlib import Path

        lambda_package = Path("../lambda/lambda-package.zip")

        if lambda_package.exists():
            code = lambda_.Code.from_asset(str(lambda_package))
        else:
            code = lambda_.Code.from_asset(
                "../lambda",
                bundling={
                    "image": lambda_.Runtime.PYTHON_3_12.bundling_image,
                    "command": [
                        "bash",
                        "-c",
                        (
                            "pip install -r requirements.txt -t /asset-output && "
                            "cp -au *.py /asset-output/"
                        ),
                    ],
                },
            )

        orchestrator = lambda_.Function(
            self,
            "WhatsAppOrchestrator",
            runtime=lambda_.Runtime.PYTHON_3_12,
            handler="whatsapp_orchestrator.handler",
            code=code,
            timeout=Duration.seconds(30),
            memory_size=512,
            architecture=lambda_.Architecture.ARM_64,
            environment=env_vars,
            tracing=lambda_.Tracing.ACTIVE,
        )

        # Create version on each deployment (triggers new execution environment)
        version = orchestrator.current_version

        # Create alias pointing to latest version (enables zero-downtime updates)
        alias = lambda_.Alias(
            self,
            "WhatsAppOrchestratorLive",
            alias_name="live",
            version=version,
            description="Live alias for zero-downtime deployments",
        )

        # Subscribe alias (not function) to SNS for zero-downtime updates
        whatsapp_topic.add_subscription(subscriptions.LambdaSubscription(alias))

        # Permissions
        orchestrator.add_to_role_policy(
            iam.PolicyStatement(
                actions=["bedrock-agentcore:InvokeAgentRuntime"],
                resources=[
                    agentcore_runtime_arn,
                    f"{agentcore_runtime_arn}/runtime-endpoint/*",
                ],
            )
        )

        orchestrator.add_to_role_policy(
            iam.PolicyStatement(
                actions=["social-messaging:SendWhatsAppMessage"],
                resources=["*"],
            )
        )

        orchestrator.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "xray:PutTraceSegments",
                    "xray:PutTelemetryRecords",
                ],
                resources=["*"],
            )
        )

        whatsapp_secret.grant_read(orchestrator)

        # Custom Resource to configure WhatsApp event destination
        if whatsapp_business_account_id:
            config_handler = lambda_.Function(
                self,
                "WhatsAppConfigHandler",
                runtime=lambda_.Runtime.PYTHON_3_12,
                handler="index.handler",
                code=lambda_.Code.from_inline("""
import boto3

client = boto3.client('socialmessaging')

def handler(event, context):
    request_type = event['RequestType']
    waba_id = event['ResourceProperties']['WabaId']
    sns_arn = event['ResourceProperties']['SnsTopicArn']

    if request_type in ['Create', 'Update']:
        client.put_whatsapp_business_account_event_destinations(
            id=waba_id,
            eventDestinations=[{
                'eventDestinationArn': sns_arn
            }]
        )

    return {'PhysicalResourceId': f'whatsapp-config-{waba_id}'}
"""),
                timeout=Duration.seconds(30),
            )

            config_handler.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "social-messaging:PutWhatsAppBusinessAccountEventDestinations",
                    ],
                    resources=["*"],
                )
            )

            provider = Provider(
                self,
                "WhatsAppConfigProvider",
                on_event_handler=config_handler,
            )

            CustomResource(
                self,
                "WhatsAppEventDestination",
                service_token=provider.service_token,
                properties={
                    "WabaId": whatsapp_business_account_id,
                    "SnsTopicArn": whatsapp_topic.topic_arn,
                },
            )

        # Outputs
        CfnOutput(self, "SNSTopicArn", value=whatsapp_topic.topic_arn)
        CfnOutput(self, "OrchestratorName", value=orchestrator.function_name)
        CfnOutput(
            self,
            "OrchestratorAliasArn",
            value=alias.function_arn,
            description="Live alias ARN for zero-downtime deployments",
        )
        CfnOutput(
            self, "OrchestratorVersion", value=version.version, description="Current Lambda version"
        )
        CfnOutput(self, "SecretArn", value=whatsapp_secret.secret_arn)
        CfnOutput(self, "SessionBucketName", value=session_bucket.bucket_name)

        # Grant AgentCore execution role access to session bucket
        agentcore_role_name = "AmazonBedrockAgentCoreSDKRuntime-us-east-1-d793631704"
        agentcore_role = iam.Role.from_role_name(self, "AgentCoreRole", agentcore_role_name)
        session_bucket.grant_read_write(agentcore_role)
