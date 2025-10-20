#!/bin/bash
# Deploy Knowledge Base with S3 Vectors via AWS CLI
# S3 Vectors not yet supported in CloudFormation

set -e

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"
BUCKET_NAME="restaurant-kb-${ACCOUNT_ID}"

echo "🚀 Deploying Restaurant Knowledge Base with S3 Vectors..."
echo "Account: $ACCOUNT_ID"
echo "Region: $REGION"
echo ""

# 1. Create S3 bucket
echo "📦 Creating S3 bucket: $BUCKET_NAME"
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket already exists"
aws s3api put-bucket-versioning --bucket $BUCKET_NAME --versioning-configuration Status=Enabled
aws s3api put-public-access-block --bucket $BUCKET_NAME \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# 2. Create IAM role for KB
echo "🔐 Creating IAM role for Knowledge Base..."
ROLE_NAME="BedrockKBRole-restaurant"

# Create trust policy
cat > /tmp/kb-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "bedrock.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

# Create role
aws iam create-role \
  --role-name $ROLE_NAME \
  --assume-role-policy-document file:///tmp/kb-trust-policy.json \
  2>/dev/null || echo "Role already exists"

# Attach S3 policy
cat > /tmp/kb-s3-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket",
      "s3:DeleteObject"
    ],
    "Resource": [
      "arn:aws:s3:::${BUCKET_NAME}",
      "arn:aws:s3:::${BUCKET_NAME}/*"
    ]
  }]
}
EOF

aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name S3Access \
  --policy-document file:///tmp/kb-s3-policy.json

ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
echo "Role ARN: $ROLE_ARN"

# Wait for role to propagate
echo "⏳ Waiting for IAM role to propagate..."
sleep 10

# 3. Create Knowledge Base
echo "🧠 Creating Knowledge Base with S3 Vectors..."
KB_RESPONSE=$(aws bedrock-agent create-knowledge-base \
  --name "restaurant-info" \
  --role-arn "$ROLE_ARN" \
  --knowledge-base-configuration '{
    "type": "VECTOR",
    "vectorKnowledgeBaseConfiguration": {
      "embeddingModelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v2:0"
    }
  }' \
  --storage-configuration '{
    "type": "S3_VECTORS",
    "s3VectorsConfiguration": {
      "vectorBucketArn": "arn:aws:s3:::'$BUCKET_NAME'",
      "indexName": "restaurant-index"
    }
  }' \
  --region $REGION \
  --output json)

KB_ID=$(echo $KB_RESPONSE | jq -r '.knowledgeBase.knowledgeBaseId')
KB_ARN=$(echo $KB_RESPONSE | jq -r '.knowledgeBase.knowledgeBaseArn')

echo "✅ Knowledge Base created!"
echo "KB ID: $KB_ID"
echo "KB ARN: $KB_ARN"

# 4. Create Data Source
echo "📚 Creating Data Source..."
DS_RESPONSE=$(aws bedrock-agent create-data-source \
  --knowledge-base-id "$KB_ID" \
  --name "restaurant-data" \
  --data-source-configuration '{
    "type": "S3",
    "s3Configuration": {
      "bucketArn": "arn:aws:s3:::'$BUCKET_NAME'",
      "inclusionPrefixes": ["data/"]
    }
  }' \
  --region $REGION \
  --output json)

DS_ID=$(echo $DS_RESPONSE | jq -r '.dataSource.dataSourceId')

echo "✅ Data Source created!"
echo "DS ID: $DS_ID"

# 5. Save outputs
echo ""
echo "📝 Saving outputs to .kb-outputs..."
cat > .kb-outputs << EOF
KB_ID=$KB_ID
KB_ARN=$KB_ARN
DS_ID=$DS_ID
BUCKET_NAME=$BUCKET_NAME
ROLE_ARN=$ROLE_ARN
EOF

echo ""
echo "✅ Knowledge Base deployment complete!"
echo ""
echo "Next steps:"
echo "1. Upload data: aws s3 sync data/restaurant/ s3://$BUCKET_NAME/data/"
echo "2. Start ingestion: aws bedrock-agent start-ingestion-job --knowledge-base-id $KB_ID --data-source-id $DS_ID"
