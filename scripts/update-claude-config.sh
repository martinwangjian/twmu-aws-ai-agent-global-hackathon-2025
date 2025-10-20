#!/bin/bash
set -e

# Load credentials from .env
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Get Cognito Client ID and refresh token
CLIENT_ID="qli2ric7jaush0pjstogu4vua"
REFRESH_TOKEN=$(grep "^COGNITO_REFRESH_TOKEN=" .env | cut -d'=' -f2-)

if [ -z "$REFRESH_TOKEN" ]; then
    echo "❌ COGNITO_REFRESH_TOKEN not found in .env"
    echo "Run: ./scripts/get_refresh_token_direct.sh"
    exit 1
fi

# Get A2A runtime ARN
A2A_ARN=$(cat .agentcore-a2a-arn 2>/dev/null || echo "")
if [ -z "$A2A_ARN" ]; then
    echo "❌ A2A runtime ARN not found. Deploy A2A agent first."
    exit 1
fi

# Convert ARN to invocation URL with FULL URL encoding (including /)
A2A_URL="https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/$(echo "$A2A_ARN" | sed 's/:/%3A/g' | sed 's/\//%2F/g')/invocations/"

# Get project directory
PROJECT_DIR=$(pwd)

# Get actual uv path
UV_PATH=$(which uv)

# Update Claude Desktop config with auto-refresh credentials
cat > ~/Library/Application\ Support/Claude/claude_desktop_config.json << CONFIGEOF
{
  "mcpServers": {
    "a2a-orchestrator": {
      "command": "${UV_PATH}",
      "args": [
        "run",
        "--directory",
        "$PROJECT_DIR",
        "python",
        "mcp_server/a2a_orchestrator_mcp.py"
      ],
      "env": {
        "AWS_REGION": "us-east-1",
        "A2A_AGENT_URL": "${A2A_URL}",
        "COGNITO_CLIENT_ID": "${CLIENT_ID}",
        "COGNITO_REFRESH_TOKEN": "${REFRESH_TOKEN}"
      }
    }
  }
}
CONFIGEOF

echo "✅ Updated Claude Desktop config with refresh token"
echo "🔗 A2A URL: $A2A_URL"
echo "📍 UV path: $UV_PATH"
echo "🔄 Refresh token valid for 60 days (no AWS credentials needed)"
echo "🔄 Please restart Claude Desktop"
