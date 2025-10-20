#!/bin/bash
# Test A2A server locally

set -e

echo "🧪 Testing A2A Server Locally..."
echo ""

# Test 1: Agent Card
echo "1️⃣ Testing agent card endpoint..."
curl -s http://localhost:9000/.well-known/agent-card.json | jq .
echo ""

# Test 2: JSON-RPC Invocation
echo "2️⃣ Testing JSON-RPC invocation..."
curl -X POST http://localhost:9000 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "req-001",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{
          "kind": "text",
          "text": "Find Italian restaurants in Mauritius with vegetarian options"
        }],
        "messageId": "12345678-1234-1234-1234-123456789012"
      }
    }
  }' | jq .

echo ""
echo "✅ Local tests complete!"
