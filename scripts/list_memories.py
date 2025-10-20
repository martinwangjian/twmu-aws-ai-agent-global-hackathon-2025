#!/usr/bin/env python3
# ruff: noqa: T201, E402
"""List existing AgentCore memories."""

from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)

from bedrock_agentcore.memory import MemoryClient

client = MemoryClient(region_name="us-east-1")

print("Existing memories:\n")
for memory in client.list_memories():
    print(f"Name: {memory.get('name')}")
    print(f"ARN: {memory.get('arn')}")
    print(f"ID: {memory.get('id')}")
    print(f"Status: {memory.get('status')}")
    print("-" * 70)
