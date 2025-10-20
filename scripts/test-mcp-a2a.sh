#!/bin/bash
# Test MCP A2A server

set -e

echo "🧪 Testing MCP A2A Server..."
echo ""

# Source AWS credentials
source .env

# Test 1: List tools
echo "1️⃣ Testing tools/list..."
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | \
  docker run -i --rm \
    -e AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY \
    -e AWS_SESSION_TOKEN \
    -e AWS_REGION \
    a2a-orchestrator-mcp | jq .

echo ""
echo "✅ MCP server test complete!"
echo ""
echo "📋 Next: Update Claude Desktop config and test booking"
