#!/bin/bash
# Test MCP server directly

cd /Users/martinwang/workspace/TWMU/gen_ai/whatsapp-bot/aws-ai-agent-global-hackathon-2025
source .env

echo "🧪 Testing MCP Server..."
echo ""

# Test if server starts
timeout 2 uv run python mcp_server/a2a_orchestrator_mcp.py 2>&1 &
PID=$!
sleep 1

if ps -p $PID > /dev/null; then
    echo "✅ MCP server is running (PID: $PID)"
    kill $PID 2>/dev/null
else
    echo "❌ MCP server failed to start"
    exit 1
fi

echo ""
echo "📋 Claude Desktop Config:"
echo "Location: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "✅ MCP server is ready!"
echo "🔄 Restart Claude Desktop to load the server"
