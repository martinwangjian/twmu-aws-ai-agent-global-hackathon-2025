#!/bin/bash
# Get Cognito OAuth bearer token for A2A agent authentication

set -e

# Get Cognito details from CDK outputs
POOL_ID=$(aws cloudformation describe-stacks \
  --stack-name CognitoStack \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
  --output text)

CLIENT_ID=$(aws cloudformation describe-stacks \
  --stack-name CognitoStack \
  --region us-east-1 \
  --query 'Stacks[0].Outputs[?OutputKey==`ClientId`].OutputValue' \
  --output text)

# Check if user exists, create if not
if ! aws cognito-idp admin-get-user \
  --user-pool-id "$POOL_ID" \
  --username "a2a-client" \
  --region us-east-1 &>/dev/null; then

  echo "Creating Cognito user..." >&2

  # Create user
  aws cognito-idp admin-create-user \
    --user-pool-id "$POOL_ID" \
    --username "a2a-client" \
    --temporary-password "TempPass123!" \
    --region us-east-1 \
    --message-action SUPPRESS >/dev/null

  # Set permanent password
  aws cognito-idp admin-set-user-password \
    --user-pool-id "$POOL_ID" \
    --username "a2a-client" \
    --password "A2AClient2025!" \
    --region us-east-1 \
    --permanent >/dev/null
fi

# Get bearer token
TOKEN=$(aws cognito-idp initiate-auth \
  --client-id "$CLIENT_ID" \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME='a2a-client',PASSWORD='A2AClient2025!' \
  --region us-east-1 \
  --query 'AuthenticationResult.AccessToken' \
  --output text)

# Save to .env
if grep -q "^COGNITO_BEARER_TOKEN=" .env 2>/dev/null; then
  sed -i.bak "s|^COGNITO_BEARER_TOKEN=.*|COGNITO_BEARER_TOKEN=$TOKEN|" .env
else
  echo "COGNITO_BEARER_TOKEN=$TOKEN" >> .env
fi

echo "$TOKEN"
