#!/usr/bin/env python3
"""Fetch A2A agent card from AgentCore Runtime"""

from urllib.parse import quote

# Get ARN from file
arn_file = ".agentcore-a2a-arn"
with open(arn_file) as f:
    agent_arn = f.read().strip()

print(f"Agent ARN: {agent_arn}")

# Construct URL
escaped_arn = quote(agent_arn, safe="")
url = f"https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/{escaped_arn}/invocations/.well-known/agent-card.json"

print(f"\nAgent Card URL:\n{url}")
print("\nTo fetch with curl:")
print(f'curl "{url}"')
