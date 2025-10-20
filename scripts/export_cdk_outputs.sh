#!/bin/bash
# Export CDK outputs to .env.cdk file for AgentCore deployment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env.cdk"

echo "📋 Exporting CDK outputs to $ENV_FILE..."

# Source main .env for AWS credentials
set -a
source "$PROJECT_ROOT/.env"
set +a

# Get CDK outputs
SESSION_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name WhatsAppStack \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`SessionBucketName`].OutputValue' \
  --output text 2>/dev/null || echo "")

# Get from .env
GOOGLE_CALENDAR_ID=$(grep "^GOOGLE_CALENDAR_ID" "$PROJECT_ROOT/.env" | cut -d'=' -f2 | tr -d '"')
AWS_REGION=$(grep "^AWS_REGION" "$PROJECT_ROOT/.env" | cut -d'=' -f2 | tr -d '"')

# Get from .bedrock_agentcore.yaml
BEDROCK_AGENTCORE_MEMORY_ID=$(grep "memory_id:" "$PROJECT_ROOT/.bedrock_agentcore.yaml" | head -1 | awk '{print $2}')
BEDROCK_AGENTCORE_MEMORY_NAME=$(grep "memory_name:" "$PROJECT_ROOT/.bedrock_agentcore.yaml" | head -1 | awk '{print $2}')

# Write to .env.cdk
cat > "$ENV_FILE" << EOF
# Auto-generated from CDK outputs - DO NOT EDIT MANUALLY
# Generated: $(date)
SESSION_BUCKET=$SESSION_BUCKET
GOOGLE_CALENDAR_ID=$GOOGLE_CALENDAR_ID
AWS_REGION=$AWS_REGION
BEDROCK_AGENTCORE_MEMORY_ID=$BEDROCK_AGENTCORE_MEMORY_ID
BEDROCK_AGENTCORE_MEMORY_NAME=$BEDROCK_AGENTCORE_MEMORY_NAME
EOF

echo "✅ CDK outputs exported:"
echo "   SESSION_BUCKET=$SESSION_BUCKET"
echo "   GOOGLE_CALENDAR_ID=$GOOGLE_CALENDAR_ID"
echo "   AWS_REGION=$AWS_REGION"
echo "   BEDROCK_AGENTCORE_MEMORY_ID=$BEDROCK_AGENTCORE_MEMORY_ID"
echo "   BEDROCK_AGENTCORE_MEMORY_NAME=$BEDROCK_AGENTCORE_MEMORY_NAME"
