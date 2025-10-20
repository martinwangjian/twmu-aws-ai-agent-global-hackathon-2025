#!/usr/bin/env python3
"""
MCP Server for A2A Agent Discovery and Communication

Uses direct A2A client for raw response passthrough (Approach 3).
No Agent wrapper = No response fabrication.
"""

import asyncio
import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import boto3
import httpx
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, Role, TextPart
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

BOOKING_AGENT_URL = os.getenv(
    "A2A_AGENT_URL",
    "https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A<YOUR_AWS_ACCOUNT_ID>%3Aruntime%2F<YOUR_AGENTCORE_RUNTIME_ID>/invocations/",
)
DEFAULT_TIMEOUT = 300  # 5 minutes

# Token cache
_token_cache: dict[str, str | datetime | None] = {"token": None, "expires_at": None}


def get_cognito_token() -> str:
    """Get Cognito token with automatic refresh using refresh token."""

    now = datetime.now(UTC)

    # Return cached token if still valid (with 5-minute buffer)
    if (
        _token_cache["token"]
        and _token_cache["expires_at"]
        and now < _token_cache["expires_at"] - timedelta(minutes=5)  # type: ignore[operator]
    ):
        return str(_token_cache["token"])

    # Get credentials from environment
    refresh_token = os.getenv("COGNITO_REFRESH_TOKEN")
    client_id = os.getenv("COGNITO_CLIENT_ID")
    region = os.getenv("AWS_REGION", "us-east-1")

    if not client_id:
        raise ValueError("COGNITO_CLIENT_ID not set in environment")
    if not refresh_token:
        raise ValueError("COGNITO_REFRESH_TOKEN not set in environment")

    # Get new token using refresh token (no AWS credentials needed)
    cognito = boto3.client("cognito-idp", region_name=region)
    response = cognito.initiate_auth(
        ClientId=client_id,
        AuthFlow="REFRESH_TOKEN_AUTH",
        AuthParameters={"REFRESH_TOKEN": refresh_token},
    )

    token = str(response["AuthenticationResult"]["IdToken"])
    expires_in = int(response["AuthenticationResult"]["ExpiresIn"])

    # Cache token
    _token_cache["token"] = token
    _token_cache["expires_at"] = now + timedelta(seconds=expires_in)

    return token


# Mock restaurant database - DEMO ONLY: La Bella Vita
MOCK_RESTAURANTS = """Found 1 Italian restaurant in Mauritius with vegetarian options:

**La Bella Vita** ($$$)
- Cuisine: Italian
- Location: Grand Baie, Mauritius
- Features: window seating, ocean view, romantic ambiance
- Vegetarian options: Yes
- Perfect for: Romantic dinners for 2 people

This is the only restaurant available for booking via this system."""

app = Server("a2a-orchestrator")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List orchestrator tools."""
    return [
        Tool(
            name="discover_restaurants",
            description=(
                "Search for restaurants in Mauritius by cuisine, location, or dietary needs"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": (
                            "Search criteria (e.g., 'Italian restaurants with vegetarian options')"
                        ),
                    }
                },
                "required": ["request"],
            },
        ),
        Tool(
            name="book_restaurant",
            description="Book a table at a specific restaurant",
            inputSchema={
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": (
                            "Booking request with restaurant name, date, time, party size"
                        ),
                    }
                },
                "required": ["request"],
            },
        ),
        Tool(
            name="approve_payment",
            description="Approve a pending payment for a booking (human-in-the-loop)",
            inputSchema={
                "type": "object",
                "properties": {
                    "booking_id": {
                        "type": "string",
                        "description": "Booking ID from payment request",
                    }
                },
                "required": ["booking_id"],
            },
        ),
    ]


@app.call_tool()
async def handle_tool(name: str, arguments: dict) -> list[TextContent]:  # noqa: PLR0912
    """Handle tool calls using direct A2A client with Bearer token."""
    request_text = arguments.get("request", "")

    if name == "discover_restaurants":
        return [TextContent(type="text", text=MOCK_RESTAURANTS)]

    if name == "approve_payment":
        booking_id = arguments.get("booking_id")
        if not booking_id:
            return [TextContent(type="text", text="Error: booking_id required")]
        request_text = f"Approve payment for booking {booking_id}"

    try:
        # Get fresh token (auto-refreshes if expired)
        bearer_token = get_cognito_token()
        session_id = str(uuid4())

        # Use OAuth Bearer token authentication
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": session_id,
        }

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, headers=headers) as httpx_client:
            # Get agent card from AgentCore Runtime (like AWS example)
            resolver = A2ACardResolver(httpx_client=httpx_client, base_url=BOOKING_AGENT_URL)
            agent_card = await resolver.get_agent_card()

            config = ClientConfig(httpx_client=httpx_client, streaming=False)
            factory = ClientFactory(config)
            client = factory.create(agent_card)

            msg = Message(
                kind="message",
                role=Role.user,
                parts=[Part(TextPart(kind="text", text=request_text))],
                message_id=uuid4().hex,
            )

            response_text = ""
            async for event in client.send_message(msg):
                if isinstance(event, tuple) and len(event) >= 1:
                    task = event[0]
                    # Extract from task artifacts
                    if hasattr(task, "artifacts"):
                        for artifact in task.artifacts:
                            if hasattr(artifact, "parts"):
                                for part in artifact.parts:
                                    # Part wraps TextPart in .root
                                    if hasattr(part, "root") and hasattr(part.root, "text"):
                                        response_text += part.root.text

        if response_text:
            return [TextContent(type="text", text=response_text)]
        return [TextContent(type="text", text="No response received from agent")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}", isError=True)]


async def main():
    """Run MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
