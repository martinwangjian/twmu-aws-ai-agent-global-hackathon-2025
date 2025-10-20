# Copyright (C) 2025 Teamwork Mauritius
# AGPL-3.0 License

"""CDK Stack for Bedrock Knowledge Base with S3 Vectors."""

from aws_cdk import CfnOutput, RemovalPolicy, Stack
from aws_cdk import aws_bedrock as bedrock
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ssm as ssm
from constructs import Construct


class RestaurantKBStack(Stack):
    """Restaurant Knowledge Base stack with S3 Vectors storage."""

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # S3 bucket for data source and vector storage
        kb_bucket = s3.Bucket(
            self,
            "RestaurantKB",
            bucket_name=f"restaurant-kb-{self.account}",
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            removal_policy=RemovalPolicy.RETAIN,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        # IAM role for Knowledge Base
        kb_role = iam.Role(
            self,
            "KBRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            description="Role for Bedrock Knowledge Base to access S3",
        )

        # Grant KB role access to bucket
        kb_bucket.grant_read_write(kb_role)

        # Add S3 Vectors permissions (required for S3_VECTORS storage type)
        kb_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3vectors:*"],
                resources=["*"],
            )
        )

        # Knowledge Base with S3 Vectors
        embedding_model_arn = (
            "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
        )
        kb = bedrock.CfnKnowledgeBase(
            self,
            "KB",
            name="restaurant-info",
            role_arn=kb_role.role_arn,
            knowledge_base_configuration={
                "type": "VECTOR",
                "vectorKnowledgeBaseConfiguration": {"embeddingModelArn": embedding_model_arn},
            },
            storage_configuration={
                "type": "S3_VECTORS",
                "s3VectorsConfiguration": {
                    "bucketArn": kb_bucket.bucket_arn,
                    "vectorIndexName": "restaurant-index",
                },
            },
        )

        # Data Source
        data_source = bedrock.CfnDataSource(
            self,
            "DataSource",
            knowledge_base_id=kb.attr_knowledge_base_id,
            name="restaurant-data",
            data_source_configuration={
                "type": "S3",
                "s3Configuration": {
                    "bucketArn": kb_bucket.bucket_arn,
                    "inclusionPrefixes": ["data/"],
                },
            },
        )

        # Store in SSM Parameter Store
        ssm.StringParameter(
            self,
            "KBIdParam",
            parameter_name="/restaurant-booking/kb-id",
            string_value=kb.attr_knowledge_base_id,
            description="Bedrock Knowledge Base ID",
        )

        ssm.StringParameter(
            self,
            "KBArnParam",
            parameter_name="/restaurant-booking/kb-arn",
            string_value=kb.attr_knowledge_base_arn,
            description="Bedrock Knowledge Base ARN",
        )

        # Outputs
        CfnOutput(self, "KnowledgeBaseId", value=kb.attr_knowledge_base_id)
        CfnOutput(self, "KnowledgeBaseArn", value=kb.attr_knowledge_base_arn)
        CfnOutput(self, "BucketName", value=kb_bucket.bucket_name)
        CfnOutput(self, "DataSourceId", value=data_source.attr_data_source_id)
