#!/usr/bin/env python3
# ruff: noqa: T201, DTZ005
"""Test memory integration with AgentCore."""

import json
import os
import sys
from datetime import datetime

import boto3

# Load environment
from dotenv import load_dotenv

load_dotenv()

agentcore = boto3.client("bedrock-agentcore", region_name="us-east-1")


def test_memory_persistence():
    """Test that memory persists across invocations."""
    runtime_arn = os.getenv("AGENTCORE_RUNTIME_ARN")
    if not runtime_arn:
        with open(".agentcore-runtime-arn") as f:
            runtime_arn = f.read().strip()

    actor_id = "23012345678"  # Test phone number (without + prefix)
    session_id = f"whatsapp-test-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    print(f"🧪 Testing memory with actor: {actor_id}")
    print(f"   Session: {session_id}\n")

    # Test 1: First message
    print("📝 Test 1: Storing information...")
    response1 = agentcore.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=session_id,
        payload=json.dumps(
            {
                "prompt": "My name is John and I prefer vegetarian food",
                "actor_id": actor_id,
                "session_id": session_id,
            }
        ),
    )
    result1 = json.loads(response1["response"].read())
    print(f"   Response: {result1.get('result', 'N/A')}\n")

    # Test 2: Recall information
    print("🔍 Test 2: Recalling information...")
    response2 = agentcore.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=session_id,
        payload=json.dumps(
            {
                "prompt": "What's my name and food preference?",
                "actor_id": actor_id,
                "session_id": session_id,
            }
        ),
    )
    result2 = json.loads(response2["response"].read())
    print(f"   Response: {result2.get('result', 'N/A')}\n")

    # Test 3: New session, same actor (cross-session memory)
    new_session = f"whatsapp-test-session-{datetime.now().strftime('%Y%m%d-%H%M%S')}-2"
    print(f"🔄 Test 3: New session ({new_session})...")
    response3 = agentcore.invoke_agent_runtime(
        agentRuntimeArn=runtime_arn,
        runtimeSessionId=new_session,
        payload=json.dumps(
            {
                "prompt": "Do you remember my food preference?",
                "actor_id": actor_id,
                "session_id": new_session,
            }
        ),
    )
    result3 = json.loads(response3["response"].read())
    print(f"   Response: {result3.get('result', 'N/A')}\n")

    print("✅ Memory test complete!")


if __name__ == "__main__":
    try:
        test_memory_persistence()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
