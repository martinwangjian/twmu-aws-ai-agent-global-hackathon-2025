#!/usr/bin/env python3
"""Update Gateway to use Lambda function instead of direct Google Calendar OAuth."""

import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import boto3
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient

# Load config
config_path = project_root / "gateway_config.json"
if not config_path.exists():
    print("❌ gateway_config.json not found!")
    exit(1)

config = json.loads(config_path.read_text())

print("=" * 80)
print("UPDATING GATEWAY TO USE LAMBDA")
print("=" * 80)

# Get Lambda ARN from CloudFormation
cfn = boto3.client("cloudformation", region_name=config["region"])
lambda_client = boto3.client("lambda", region_name=config["region"])

try:
    response = cfn.describe_stacks(StackName="CalendarServiceStack")
    stack = response["Stacks"][0]

    # Find Lambda function name from resources
    resources = cfn.describe_stack_resources(StackName="CalendarServiceStack")
    lambda_function_name = None
    for resource in resources["StackResources"]:
        if resource["ResourceType"] == "AWS::Lambda::Function":
            lambda_function_name = resource["PhysicalResourceId"]
            break

    if not lambda_function_name:
        print("❌ Could not find Lambda function in CalendarServiceStack")
        exit(1)

    # Get full Lambda ARN
    lambda_response = lambda_client.get_function(FunctionName=lambda_function_name)
    lambda_arn = lambda_response["Configuration"]["FunctionArn"]

    print(f"✓ Found Lambda ARN: {lambda_arn}")

except Exception as e:
    print(f"❌ CalendarServiceStack not found: {e}")
    print("\nPlease deploy the stack first:")
    print("  cd cdk_infra")
    print("  uv run cdk deploy CalendarServiceStack")
    exit(1)

# Initialize Gateway client
client = GatewayClient(region_name=config["region"])
gateway = client.client.get_gateway(gatewayIdentifier=config["gateway_id"])

# Delete old target if exists
if "calendar_target_id" in config:
    print(f"\nDeleting old target: {config['calendar_target_id']}")
    try:
        client.client.delete_gateway_target(
            gatewayIdentifier=config["gateway_id"], targetId=config["calendar_target_id"]
        )
        print("✓ Old target deleted")
    except Exception as e:
        print(f"⚠️  Could not delete old target: {e}")

# Create Lambda target with tool schema
print("\nCreating Lambda target...")

# Define tool schema for Lambda
tool_schema = [
    {
        "name": "checkAvailability",
        "description": "Check if a time slot is available for booking",
        "inputSchema": {
            "type": "object",
            "properties": {
                "calendarId": {"type": "string", "description": "Calendar ID"},
                "start": {"type": "string", "description": "Start time ISO 8601"},
                "end": {"type": "string", "description": "End time ISO 8601"},
            },
            "required": ["calendarId", "start", "end"],
        },
    },
    {
        "name": "getAvailableSlots",
        "description": "Get available time slots for a date",
        "inputSchema": {
            "type": "object",
            "properties": {
                "calendarId": {"type": "string", "description": "Calendar ID"},
                "date": {"type": "string", "description": "Date YYYY-MM-DD"},
                "duration": {"type": "integer", "description": "Duration in minutes (default 120)"},
            },
            "required": ["calendarId", "date"],
        },
    },
    {
        "name": "createEvent",
        "description": "Create a booking event in Google Calendar",
        "inputSchema": {
            "type": "object",
            "properties": {
                "calendarId": {"type": "string", "description": "Calendar ID"},
                "summary": {"type": "string", "description": "Event title"},
                "description": {"type": "string", "description": "Event description"},
                "start": {"type": "string", "description": "Start time ISO 8601"},
                "end": {"type": "string", "description": "End time ISO 8601"},
            },
            "required": ["calendarId", "summary", "start", "end"],
        },
    },
    {
        "name": "listEvents",
        "description": "List calendar events",
        "inputSchema": {
            "type": "object",
            "properties": {
                "calendarId": {"type": "string"},
                "timeMin": {"type": "string"},
                "timeMax": {"type": "string"},
                "maxResults": {"type": "integer"},
            },
            "required": ["calendarId"],
        },
    },
    {
        "name": "deleteEvent",
        "description": "Delete a calendar event",
        "inputSchema": {
            "type": "object",
            "properties": {"calendarId": {"type": "string"}, "eventId": {"type": "string"}},
            "required": ["calendarId", "eventId"],
        },
    },
]

target = client.create_mcp_gateway_target(
    gateway=gateway,
    name="GoogleCalendarLambda",
    target_type="lambda",
    target_payload={"lambdaArn": lambda_arn, "toolSchema": {"inlinePayload": tool_schema}},
    credentials=None,  # No credentials needed - Lambda has service account
)

# Update config
config["calendar_target_id"] = target["targetId"]
config["calendar_lambda_arn"] = lambda_arn
config_path.write_text(json.dumps(config, indent=2))

print("=" * 80)
print("✅ GATEWAY UPDATED!")
print("=" * 80)
print(f"Target ID: {target['targetId']}")
print(f"Lambda ARN: {lambda_arn}")
print("\nAvailable tools:")
print("  - createEvent: Create booking")
print("  - listEvents: List bookings")
print("  - deleteEvent: Cancel booking")
print("\nTest booking:")
print("  uv run python scripts/test_gateway_booking.py")
print("=" * 80)
