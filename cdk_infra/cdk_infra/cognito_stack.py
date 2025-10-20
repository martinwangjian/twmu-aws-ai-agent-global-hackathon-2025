"""Cognito User Pool for A2A Agent Authentication."""

from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_cognito as cognito
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class CognitoStack(Stack):
    """Cognito User Pool for AgentCore A2A Runtime authentication."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # User pool for A2A agent authentication
        user_pool = cognito.UserPool(
            self,
            "A2AUserPool",
            user_pool_name="a2a-booking-agent-users",
            self_sign_up_enabled=False,
            sign_in_aliases=cognito.SignInAliases(username=True),
            password_policy=cognito.PasswordPolicy(min_length=8),
            removal_policy=RemovalPolicy.DESTROY,
        )

        # App client for authentication
        app_client = user_pool.add_client(
            "A2AClient",
            user_pool_client_name="a2a-booking-client",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(
                user_password=True,
                custom=False,
                user_srp=False,
            ),
        )

        # Store in SSM Parameter Store
        discovery_url = f"https://cognito-idp.{self.region}.amazonaws.com/{user_pool.user_pool_id}/.well-known/openid-configuration"

        ssm.StringParameter(
            self,
            "ClientIdParam",
            parameter_name="/restaurant-booking/cognito-client-id",
            string_value=app_client.user_pool_client_id,
            description="Cognito App Client ID for A2A authentication",
        )

        ssm.StringParameter(
            self,
            "DiscoveryUrlParam",
            parameter_name="/restaurant-booking/cognito-discovery-url",
            string_value=discovery_url,
            description="Cognito OpenID Discovery URL",
        )

        # Outputs
        CfnOutput(
            self,
            "UserPoolId",
            value=user_pool.user_pool_id,
            description="Cognito User Pool ID",
        )

        CfnOutput(
            self,
            "ClientId",
            value=app_client.user_pool_client_id,
            description="Cognito App Client ID",
        )

        CfnOutput(
            self,
            "DiscoveryUrl",
            value=discovery_url,
            description="OpenID Discovery URL for JWT authorizer",
        )
