#!/usr/bin/env python3
# ruff: noqa: T201, E402
"""Create AgentCore memory for WhatsApp conversations."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env BEFORE importing boto3/bedrock
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)

# Clear any cached credentials
if "AWS_SHARED_CREDENTIALS_FILE" in os.environ:
    del os.environ["AWS_SHARED_CREDENTIALS_FILE"]

from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name="us-east-1")

print("Creating memory resource (takes 2-3 minutes)...")
memory = client.create_memory_and_wait(
    name="whatsapp_conversation_memory",
    strategies=[
        {
            "summaryMemoryStrategy": {
                "name": "SessionSummarizer",
                "namespaces": ["/summaries/{actorId}/{sessionId}"],
            }
        }
    ],
)

print("\n✅ Memory created successfully!")
print(f"Memory ARN: {memory.get('arn')}")
print(f"Memory ID: {memory.get('id')}")
print("\nAdd this to .env:")
print(f"AGENTCORE_MEMORY_ARN={memory.get('arn')}")
