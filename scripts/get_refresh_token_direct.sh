#!/bin/bash
# Get Cognito refresh token without AWS credentials

set -e

CLIENT_ID="qli2ric7jaush0pjstogu4vua"
USERNAME="a2a-client"
PASSWORD="A2AClient2025!"
REGION="us-east-1"

RESPONSE=$(aws cognito-idp initiate-auth \
  --client-id "$CLIENT_ID" \
  --auth-flow USER_PASSWORD_AUTH \
  --auth-parameters USERNAME="$USERNAME",PASSWORD="$PASSWORD" \
  --region "$REGION" \
  --no-sign-request 2>&1)

if echo "$RESPONSE" | grep -q "RefreshToken"; then
  REFRESH_TOKEN=$(echo "$RESPONSE" | jq -r '.AuthenticationResult.RefreshToken')

  if grep -q "^COGNITO_REFRESH_TOKEN=" .env 2>/dev/null; then
    sed -i.bak "s|^COGNITO_REFRESH_TOKEN=.*|COGNITO_REFRESH_TOKEN=$REFRESH_TOKEN|" .env
  else
    echo "COGNITO_REFRESH_TOKEN=$REFRESH_TOKEN" >> .env
  fi

  echo "✅ Refresh token saved to .env (valid for 60 days)"
else
  echo "❌ Failed to get refresh token"
  echo "$RESPONSE"
  exit 1
fi
