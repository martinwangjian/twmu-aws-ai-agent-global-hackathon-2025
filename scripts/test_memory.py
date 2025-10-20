#!/usr/bin/env python3
"""Test AgentCore memory persistence."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import boto3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def get_agentcore_arn() -> str:
    """Get AgentCore runtime ARN."""
    arn = os.getenv("AGENTCORE_RUNTIME_ARN")
    if not arn:
        arn_file = Path(__file__).parent.parent / ".agentcore-runtime-arn"
        if arn_file.exists():
            arn = arn_file.read_text().strip()
    if not arn:
        raise ValueError("AGENTCORE_RUNTIME_ARN not set")
    return arn


def invoke_agentcore(session_id: str, prompt: str) -> str:
    """Invoke AgentCore with prompt."""
    client = boto3.client("bedrock-agentcore", region_name="us-east-1")
    runtime_arn = get_agentcore_arn()
    memory_arn = os.getenv("AGENTCORE_MEMORY_ARN")

    params = {
        "agentRuntimeArn": runtime_arn,
        "runtimeSessionId": session_id,
        "payload": json.dumps({"prompt": prompt}),
    }

    if memory_arn:
        params["memoryArn"] = memory_arn
        print(f"Using memory ARN: {memory_arn}")

    response = client.invoke_agent_runtime(**params)
    result = json.loads(response["response"].read())
    return str(result.get("result", "No response"))


def test_memory():
    """Test memory persistence."""
    session_id = f"test:{datetime.now().strftime('%Y%m%d%H%M')}"

    print("=" * 60)
    print("Testing AgentCore Memory")
    print("=" * 60)
    print(f"Session ID: {session_id}\n")

    # Test 1: Store information
    print("=== Test 1: Store Information ===")
    prompt1 = "My name is John and I prefer morning appointments at 10am"
    print(f"User: {prompt1}")
    response1 = invoke_agentcore(session_id, prompt1)
    print(f"Agent: {response1}\n")

    # Test 2: Recall information (same session)
    print("=== Test 2: Recall Information ===")
    prompt2 = "What's my name and what time do I prefer?"
    print(f"User: {prompt2}")
    response2 = invoke_agentcore(session_id, prompt2)
    print(f"Agent: {response2}\n")

    # Verify memory
    print("=== Verification ===")
    success = True

    if "john" not in response2.lower():
        print("❌ Failed: Name not remembered")
        success = False
    else:
        print("✅ Passed: Name remembered")

    if "10" not in response2 or "morning" not in response2.lower():
        print("❌ Failed: Preference not remembered")
        success = False
    else:
        print("✅ Passed: Preference remembered")

    print("\n" + "=" * 60)
    if success:
        print("✅ Memory test PASSED!")
    else:
        print("❌ Memory test FAILED!")
    print("=" * 60)

    return success


if __name__ == "__main__":
    try:
        success = test_memory()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
