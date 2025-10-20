#!/usr/bin/env bash
set -e

echo "🎨 Generating architecture diagrams..."
echo ""

DIAGRAMS_DIR="docs/architecture/diagrams"
mkdir -p "${DIAGRAMS_DIR}"

# Note: This script uses AWS Diagram MCP server
# Make sure it's configured in your MCP settings

echo "📊 Generating diagrams..."
echo ""
echo "To generate diagrams, use Amazon Q with AWS Diagram MCP:"
echo ""
echo "1. System Overview:"
echo "   'Generate AWS architecture diagram showing: User -> WhatsApp -> AWS End User Messaging -> SNS -> Lambda -> AgentCore -> Bedrock'"
echo ""
echo "2. WhatsApp Flow:"
echo "   'Generate detailed flow diagram for WhatsApp message processing with Lambda orchestrator'"
echo ""
echo "3. AgentCore Runtime:"
echo "   'Generate diagram showing AgentCore runtime with Strands Agent, MCP Client, and Bedrock integration'"
echo ""
echo "4. Deployment Pipeline:"
echo "   'Generate deployment pipeline diagram showing deploy.sh steps'"
echo ""
echo "Save generated diagrams to: ${DIAGRAMS_DIR}/"
echo ""
echo "✅ Diagram generation guide created"
