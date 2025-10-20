#!/usr/bin/env bash
set -e

echo "🔧 Setting up MCP servers for Q CLI"
echo ""

Q_MCP_CONFIG="$HOME/.config/amazonq/mcp.json"
PROJECT_MCP_CONFIG=".mcp.json"

# Backup existing Q CLI MCP config
if [ -f "$Q_MCP_CONFIG" ]; then
    echo "📦 Backing up existing Q CLI MCP config..."
    cp "$Q_MCP_CONFIG" "$Q_MCP_CONFIG.backup.$(date +%Y%m%d-%H%M%S)"
    echo "✅ Backup created"
fi

# Create Q CLI config directory
mkdir -p "$(dirname "$Q_MCP_CONFIG")"

# Copy project MCP config to Q CLI global config
echo "📋 Copying project MCP config to Q CLI..."
cp "$PROJECT_MCP_CONFIG" "$Q_MCP_CONFIG"

echo ""
echo "✅ MCP servers configured for Q CLI!"
echo ""
echo "Available MCP servers:"
echo "  • strands - Strands Agents framework"
echo "  • aws-diagram - AWS architecture diagrams"
echo "  • code-doc-gen - Code documentation"
echo "  • bedrock-agentcore - AgentCore management"
echo "  • cdk - AWS CDK best practices"
echo "  • aws-documentation - AWS service docs"
echo ""
echo "Verify with: q mcp list"
echo ""
echo "⚠️  Note: You may need to restart Q CLI for changes to take effect"
