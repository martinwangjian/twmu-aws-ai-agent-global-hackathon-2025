#!/usr/bin/env python3
# ruff: noqa: T201, E722, E501
"""Deploy Knowledge Base with S3 Vectors using boto3."""

import json
import time

import boto3

# Initialize clients
sts = boto3.client("sts", region_name="us-east-1")
s3 = boto3.client("s3", region_name="us-east-1")
iam = boto3.client("iam", region_name="us-east-1")
bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")

# Get account ID
account_id = sts.get_caller_identity()["Account"]
bucket_name = f"restaurant-kb-{account_id}"
role_name = "BedrockKBRole-restaurant"

print("🚀 Deploying Knowledge Base with boto3")
print(f"Account: {account_id}")
print(f"Bucket: {bucket_name}\n")

# 1. Ensure S3 bucket exists
print("📦 Checking S3 bucket...")
try:
    s3.head_bucket(Bucket=bucket_name)
    print(f"✅ Bucket exists: {bucket_name}")
except:
    print(f"Creating bucket: {bucket_name}")
    s3.create_bucket(Bucket=bucket_name)
    s3.put_bucket_versioning(Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"})

# 2. Ensure IAM role exists
print("\n🔐 Checking IAM role...")
role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
try:
    iam.get_role(RoleName=role_name)
    print(f"✅ Role exists: {role_name}")
except:
    print(f"Creating role: {role_name}")
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "bedrock.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }
    iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description="Role for Bedrock Knowledge Base",
    )

    # Attach S3 policy
    s3_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:ListBucket",
                    "s3:DeleteObject",
                ],
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*",
                ],
            }
        ],
    }
    iam.put_role_policy(
        RoleName=role_name, PolicyName="S3Access", PolicyDocument=json.dumps(s3_policy)
    )

    # Attach S3 Vectors policy
    s3vectors_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["s3vectors:*"],
                "Resource": "*",
            }
        ],
    }
    iam.put_role_policy(
        RoleName=role_name,
        PolicyName="S3VectorsAccess",
        PolicyDocument=json.dumps(s3vectors_policy),
    )
    print("⏳ Waiting for role to propagate...")
    time.sleep(10)

# 3. Create Knowledge Base with S3 Vectors
print("\n🧠 Creating Knowledge Base...")

# Check if KB already exists
try:
    existing_kbs = bedrock_agent.list_knowledge_bases()
    for kb in existing_kbs.get("knowledgeBaseSummaries", []):
        if kb["name"] == "restaurant-info":
            kb_id = kb["knowledgeBaseId"]
            print(f"✅ Knowledge Base already exists: {kb_id}")
            print("   Skipping creation...")

            # Save to .env
            with open(".env") as f:
                env_content = f.read()
            if "RESTAURANT_KB_ID=" not in env_content:
                with open(".env", "a") as f:
                    f.write(f"\nRESTAURANT_KB_ID={kb_id}\n")

            print("\n✅ Knowledge Base deployment complete (existing)")
            import sys

            sys.exit(0)
except Exception as e:
    print(f"⚠️  Could not check existing KBs: {e}")

embedding_arn = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
try:
    kb_response = bedrock_agent.create_knowledge_base(
        name="restaurant-info",
        roleArn=role_arn,
        knowledgeBaseConfiguration={
            "type": "VECTOR",
            "vectorKnowledgeBaseConfiguration": {"embeddingModelArn": embedding_arn},
        },
        storageConfiguration={
            "type": "S3_VECTORS",
            "s3VectorsConfiguration": {
                "vectorBucketArn": f"arn:aws:s3:::{bucket_name}",
                "indexName": "restaurant-index",
            },
        },
    )

    kb_id = kb_response["knowledgeBase"]["knowledgeBaseId"]
    kb_arn = kb_response["knowledgeBase"]["knowledgeBaseArn"]

    print("✅ Knowledge Base created!")
    print(f"   KB ID: {kb_id}")
    print(f"   KB ARN: {kb_arn}")

    # 4. Create Data Source
    print("\n📚 Creating Data Source...")
    ds_response = bedrock_agent.create_data_source(
        knowledgeBaseId=kb_id,
        name="restaurant-data",
        dataSourceConfiguration={
            "type": "S3",
            "s3Configuration": {
                "bucketArn": f"arn:aws:s3:::{bucket_name}",
                "inclusionPrefixes": ["data/"],
            },
        },
    )

    ds_id = ds_response["dataSource"]["dataSourceId"]
    print("✅ Data Source created!")
    print(f"   DS ID: {ds_id}")

    # 5. Save outputs
    print("\n📝 Saving outputs...")
    with open(".kb-outputs", "w") as f:
        f.write(f"KB_ID={kb_id}\n")
        f.write(f"KB_ARN={kb_arn}\n")
        f.write(f"DS_ID={ds_id}\n")
        f.write(f"BUCKET_NAME={bucket_name}\n")
        f.write(f"ROLE_ARN={role_arn}\n")

    print("\n✅ Deployment complete!")
    print("\nNext steps:")
    print(f"1. Add to .env: RESTAURANT_KB_ID={kb_id}")
    print("2. Start ingestion:")
    print(
        f"   aws bedrock-agent start-ingestion-job --knowledge-base-id {kb_id} --data-source-id {ds_id}"
    )

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
