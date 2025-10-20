# Copyright (C) 2025 Teamwork Mauritius
# AGPL-3.0 License

"""AgentCore agent with persistent memory and Gateway tools."""

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

import boto3
from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.runtime.context import RequestContext
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.models import BedrockModel
from strands.session.s3_session_manager import S3SessionManager
from strands.tools.mcp.mcp_client import MCPClient
from strands_tools import current_time

from .hooks import LongTermMemoryHook, MemoryConfig
from .tools import search_restaurant_info

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()
memory_config = MemoryConfig()

# Configuration
SESSION_BUCKET = os.getenv("SESSION_BUCKET", "agentcore-sessions-<YOUR_AWS_ACCOUNT_ID>")
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
# Load from environment - must be set in Dockerfile
GOOGLE_CALENDAR_ID = os.getenv(
    "GOOGLE_CALENDAR_ID",
    "f816bc2b3b70f58fcf66ac95ddb596707b9ece139b68ed226e161ddf4e57896f@group.calendar.google.com",
)

# Gateway configuration
GATEWAY_CONFIG_PATH = Path(__file__).parent.parent.parent / "gateway_config.json"

# Create boto3 session with correct region
boto_session = boto3.Session(region_name=AWS_REGION)


def clean_response(text: str) -> str:
    """Remove <think> and <thinking> tags and internal reasoning from response."""
    # Remove <think>...</think> and <thinking>...</thinking> blocks (including multiline)
    cleaned = re.sub(
        r"<think(?:ing)?>.*?</think(?:ing)?>", "", text, flags=re.DOTALL | re.IGNORECASE
    )
    # Remove extra whitespace/newlines left behind
    cleaned = re.sub(r"\n\s*\n\s*\n", "\n\n", cleaned)
    return cleaned.strip()


def get_gateway_token() -> str | None:
    """Get OAuth token for Gateway access."""
    if not GATEWAY_CONFIG_PATH.exists():
        logger.warning("Gateway config not found, Gateway tools disabled")
        return None

    config = json.loads(GATEWAY_CONFIG_PATH.read_text())
    client = GatewayClient(region_name=config["region"])
    return client.get_access_token_for_cognito(config["client_info"])  # type: ignore[no-any-return]


def create_gateway_transport(gateway_url: str, token: str) -> Any:
    """Create MCP transport for Gateway."""
    return streamablehttp_client(gateway_url, headers={"Authorization": f"Bearer {token}"})


def get_gateway_tools() -> tuple[list, Any | None]:
    """Load tools from Gateway and return tools + MCP client."""
    try:
        if not GATEWAY_CONFIG_PATH.exists():
            logger.warning("Gateway config not found, skipping Gateway tools")
            return [], None

        config = json.loads(GATEWAY_CONFIG_PATH.read_text())
        token = get_gateway_token()

        if not token:
            logger.warning("Failed to get Gateway token")
            return [], None

        mcp_client = MCPClient(lambda: create_gateway_transport(config["gateway_url"], token))
        mcp_client.__enter__()  # Start the context manager

        tools = mcp_client.list_tools_sync()
        logger.info(f"Loaded {len(tools)} tools from Gateway: {[t.tool_name for t in tools]}")
        return tools, mcp_client

    except Exception as e:
        logger.error(f"Failed to load Gateway tools: {e}")
        return [], None


def create_agent(actor_id: str, session_id: str) -> Agent:
    """Create agent with S3 session persistence, semantic memory, and Gateway tools."""
    logger.info(f"Creating agent for {actor_id}:{session_id}")

    # Load Gateway tools (keep MCP client alive)
    gateway_tools, mcp_client = get_gateway_tools()

    system_prompt = f"""You are La Bella Vita restaurant assistant on WhatsApp.

RESTAURANT INFORMATION:
- Use search_restaurant_info tool for menu, dietary options, allergens, hours, prices

BUSINESS HOURS:
- Monday-Thursday: 11:00 AM - 10:00 PM
- Friday-Saturday: 11:00 AM - 11:00 PM
- Sunday: 11:00 AM - 10:00 PM
- Time zone: Indian/Mauritius (UTC+4)

BOOKING MANAGEMENT:
**CRITICAL BOOKING RULES - MUST FOLLOW**:
1. ALWAYS use checkAvailability tool BEFORE createEvent - NO EXCEPTIONS
2. NEVER use listEvents for availability checking - use checkAvailability instead
3. If checkAvailability returns available=false, DO NOT create booking
4. Only call createEvent after checkAvailability confirms available=true
5. ALWAYS use calendarId: {GOOGLE_CALENDAR_ID}
6. NEVER use "primary" as calendar ID
7. Default booking duration: 2 hours
8. Only accept bookings during business hours
9. If time slot is unavailable, inform customer and suggest checking other times
10. Customer's phone number is ALREADY KNOWN from WhatsApp - DO NOT ask for it
11. Only collect: customer name, date, time, party size

**Booking Process (STRICT ORDER - NO SHORTCUTS ALLOWED)**:
1. Collect: customer name, date, time, party size (phone is already known)
2. Verify time is within business hours
3. **MANDATORY STEP 1**: Call checkAvailability with calendarId, start, and end times
4. **WAIT** for checkAvailability response
5. If available=false: inform customer of conflict, suggest alternatives, **STOP - DO NOT PROCEED**
6. If available=true: **MANDATORY STEP 2**: Call createEvent tool with exact same parameters
7. **WAIT** for createEvent response containing eventId
8. **ONLY AFTER** receiving real eventId from createEvent: confirm booking
9. Confirmation format: "Booking confirmed! Event ID: [real-eventId-from-response]"

**ABSOLUTE PROHIBITIONS**:
- NEVER say "booking confirmed" without calling createEvent first
- NEVER fabricate event IDs (they look like: abc123xyz456)
- NEVER skip the createEvent tool call
- NEVER assume booking succeeded without seeing the eventId response
- If you don't have a real eventId from createEvent response, say
  "I need to create the booking first"

**Event Format**:
- Summary: "Restaurant Booking - [Customer Name] ([Party Size] guests)"
- Description: Include customer phone and party size
- Use ISO 8601 format: YYYY-MM-DDTHH:MM:SS+04:00

**Smart Availability Proposals**:
- Use getAvailableSlots tool when customer asks for available times
- Queries: "show me available times", "when are you free", "what times are open"
- Provide 3-5 available time slots
- Format: "Available times for [date]: 6:00 PM, 6:30 PM, 7:30 PM, 8:00 PM, 9:00 PM"
- If customer's preferred time is unavailable, proactively suggest alternatives using this tool

**Listing Bookings**:
- Use listEvents tool to show existing bookings
- Filter by date range (default: upcoming bookings)
- Show: booking ID, customer name, date/time, party size
- Format results clearly for customer

**Canceling Bookings**:
- Use deleteEvent tool to cancel bookings
- Require confirmation before canceling
- Accept booking ID or natural description (e.g., "my booking tomorrow at 7pm")
- For "cancel all" requests: list all bookings first, then ask for explicit confirmation
- Confirm cancellation after deletion

IMPORTANT RULES:
1. ALWAYS use current_time tool first when user mentions relative dates (today, tomorrow, next week)
2. ALWAYS use search_restaurant_info for restaurant questions
3. ALWAYS check availability before booking
4. Reject bookings outside business hours
5. Be helpful when conflicts occur - proactively suggest available times
6. For cancellations, confirm which booking before deleting
7. Never cancel without customer confirmation
8. DO NOT ask for phone number - it's already known from WhatsApp
9. Keep confirmations simple - no calendar links

RESPONSE FORMAT:
- Keep all reasoning internal - do NOT include <think> or <thinking> tags in your responses
- Respond naturally and conversationally to customers
- Be friendly, professional, and helpful
- Keep responses concise and clear"""

    # Combine all tools: time + KB + Gateway
    all_tools = [current_time, search_restaurant_info] + gateway_tools

    return Agent(
        name="La Bella Vita Restaurant Agent",
        description="Restaurant booking and information agent for La Bella Vita in Mauritius",
        model=BedrockModel(model_id=MODEL_ID, boto_session=boto_session),
        system_prompt=system_prompt,
        conversation_manager=SlidingWindowConversationManager(
            window_size=100, should_truncate_results=True
        ),
        session_manager=S3SessionManager(
            session_id=session_id, bucket=SESSION_BUCKET, prefix=f"actor-{actor_id}/"
        ),
        hooks=[LongTermMemoryHook(memory_id=memory_config.memory_id)],
        tools=all_tools,
        state={"actor_id": actor_id, "session_id": session_id},
    )


@app.entrypoint
def invoke(payload: dict[str, Any], context: RequestContext | None = None) -> dict[str, Any]:
    """AgentCore entrypoint with persistent memory and Gateway tools."""
    user_message = payload.get("prompt", "Hello")
    actor_id = payload.get("actor_id", "default-user")
    session_id = (
        context.session_id
        if context and context.session_id
        else payload.get("session_id", "default")
    )

    logger.info(f"Processing: {user_message} (actor: {actor_id}, session: {session_id})")

    try:
        agent = create_agent(actor_id, session_id)
        result = agent(user_message)

        if hasattr(result, "message") and hasattr(result.message, "content"):
            content = result.message.content
            if isinstance(content, list) and len(content) > 0:
                first_item = content[0]
                response_text = first_item.text if hasattr(first_item, "text") else str(first_item)
            else:
                response_text = str(content)
        else:
            response_text = str(result)

        # Clean response to remove <think> tags
        response_text = clean_response(response_text)

        return {"result": response_text, "status": "success"}

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {"result": f"Error: {str(e)}", "status": "error"}


if __name__ == "__main__":
    # Check if running in A2A mode
    if os.getenv("A2A_MODE") == "true":
        logger.info("Starting AgentCore agent in A2A mode...")
        from strands.multiagent.a2a import A2AServer

        # Create agent for A2A
        agent = create_agent(actor_id="a2a-client", session_id="a2a-session")

        # Create A2A server
        a2a_server = A2AServer(
            agent=agent,
            host="0.0.0.0",
            port=9000,
            http_url=os.getenv("A2A_PUBLIC_URL"),
        )

        logger.info(f"A2A server starting on port 9000, public URL: {os.getenv('A2A_PUBLIC_URL')}")
        a2a_server.serve()
    else:
        logger.info("Starting AgentCore agent with Gateway tools...")
        app.run()
