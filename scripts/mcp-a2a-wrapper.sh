#!/bin/bash
# MCP A2A Wrapper - No AWS credentials needed!

# Get token using Python
BEARER_TOKEN=$(python3 << 'PYTHON_EOF'
import json, urllib.request

body = json.dumps({
    "AuthFlow": "USER_PASSWORD_AUTH",
    "ClientId": "qli2ric7jaush0pjstogu4vua",
    "AuthParameters": {
        "USERNAME": "a2a-client",
        "PASSWORD": "A2AClient2025!"
    }
}).encode()

req = urllib.request.Request(
    "https://cognito-idp.us-east-1.amazonaws.com/",
    data=body,
    headers={
        "Content-Type": "application/x-amz-json-1.1",
        "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth"
    }
)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        print(result["AuthenticationResult"]["AccessToken"])
except:
    pass
PYTHON_EOF
)

# Validate token
if [ -z "$BEARER_TOKEN" ] || [[ ! "$BEARER_TOKEN" =~ ^eyJ ]]; then
  exit 1
fi

# Run Docker
exec docker run -i --rm -e COGNITO_BEARER_TOKEN="$BEARER_TOKEN" a2a-orchestrator-mcp
