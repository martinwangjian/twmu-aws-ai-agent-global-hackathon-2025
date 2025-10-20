"""Payment Bucket Stack for AP2 Payment Tracking"""

from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from constructs import Construct


class PaymentBucketStack(Stack):
    """Stack for payment tracking S3 bucket"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket for payment tracking
        self.payment_bucket = s3.Bucket(
            self,
            "PaymentTrackingBucket",
            bucket_name="booking-agent-payments",
            versioned=False,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # Grant permissions to AgentCore execution role
        # Note: Role is created by agentcore CLI, we just reference it
        agentcore_role = iam.Role.from_role_arn(
            self,
            "AgentCoreRole",
            role_arn=f"arn:aws:iam::{self.account}:role/AmazonBedrockAgentCoreSDKRuntime-us-east-1-b1731112de",
        )

        # Grant read/write permissions
        self.payment_bucket.grant_read_write(agentcore_role)

        # Output bucket name
        CfnOutput(
            self,
            "PaymentBucketName",
            value=self.payment_bucket.bucket_name,
            description="S3 bucket for payment tracking",
        )
