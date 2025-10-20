#!/usr/bin/env python3
"""Simple test for Google Calendar features."""

import json
import subprocess
import sys


def invoke_agent(prompt: str) -> str:
    """Invoke agent and return response."""
    cmd = [
        "uv",
        "run",
        "agentcore",
        "invoke",
        json.dumps({"prompt": prompt, "actor_id": "calendar-test"}),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    # Parse response from output
    for line in result.stdout.split("\n"):
        if '"result":' in line:
            try:
                # Extract JSON from line
                start = line.find("{")
                if start >= 0:
                    response_json = json.loads(line[start:])
                    return response_json.get("result", "")
            except:
                pass
    return "Error: Could not parse response"


def main():
    """Run calendar feature tests."""

    tests = [
        ("Check Availability", "Is tomorrow at 8pm available for booking?"),
        ("Get Available Slots", "Show me available times for tomorrow"),
        (
            "Create Booking",
            "Book tomorrow at 3pm for 2 people, name Test Calendar, phone +23099999999",
        ),
        ("List Bookings", "Show me all bookings for tomorrow"),
        ("Cancel Booking", "Cancel my booking tomorrow at 3pm"),
        ("Verify Cancellation", "Show me all bookings for tomorrow"),
    ]

    for _i, (_name, prompt) in enumerate(tests, 1):

        invoke_agent(prompt)



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception:
        sys.exit(1)
