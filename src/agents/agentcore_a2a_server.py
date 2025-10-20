"""AgentCore A2A Server - Restaurant Booking Agent"""

import json
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
from fastapi import FastAPI
from strands import Agent
from strands.models import BedrockModel
from strands.multiagent.a2a import A2AServer

from agents.tools.payment_tool import approve_payment, check_payment_status, request_payment
from config.runtime_config import get_calendar_id, get_model_id

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GATEWAY_CONFIG_PATH = Path(__file__).parent.parent.parent / "gateway_config.json"

# Use runtime URL from environment variable, fallback to local
runtime_url = os.environ.get("AGENTCORE_RUNTIME_URL", "http://127.0.0.1:9000/")
logger.info(f"Runtime URL: {runtime_url}")


def load_gateway_tools():
    """Load Gateway tools via MCP"""
    from mcp.client.streamable_http import streamablehttp_client
    from strands.tools.mcp.mcp_client import MCPClient

    config = json.loads(GATEWAY_CONFIG_PATH.read_text())
    client = GatewayClient(region_name=config["region"])
    token = client.get_access_token_for_cognito(config["client_info"])

    # Create MCP transport
    def create_transport():
        return streamablehttp_client(
            config["gateway_url"], headers={"Authorization": f"Bearer {token}"}
        )

    # Create MCP client
    mcp_client = MCPClient(create_transport)
    mcp_client.__enter__()

    # Get tools
    tools = mcp_client.list_tools_sync()

    return tools, config["region"]


# Create Strands agent with Gateway tools
gateway_tools, region = load_gateway_tools()

# Get configuration from SSM Parameter Store (or .env for local dev)
calendar_id = get_calendar_id()
model_id = get_model_id()

strands_agent = Agent(
    name="La Bella Vita Restaurant Agent",
    description="Restaurant booking and information agent for La Bella Vita in Mauritius",
    model=BedrockModel(model_id=model_id, region_name=region),
    system_prompt=f"""You are La Bella Vita restaurant booking agent.

BOOKING WORKFLOW (MANDATORY):
When you receive a booking request, you MUST:
1. Parse: date, time, party size, preferences from request
2. Call checkAvailability with calendarId="{calendar_id}", start, end times
3. If available=true: Call createEvent with same parameters
4. Return ONLY the real eventId from createEvent response
5. If available=false: Inform user of conflict

PAYMENT WORKFLOW (AP2 Protocol - Human-in-the-Loop):
For ALL bookings, you MUST request payment deposit:
1. After successful createEvent, ALWAYS call request_payment
2. Amount: $5 USD per person (USDC stablecoin)
3. Use eventId as booking_id
4. Return payment details with booking_id to human
5. WAIT for human to call approve_payment(booking_id)
6. Do NOT confirm booking until payment is approved
7. Do NOT auto-confirm payments

CALENDAR PARAMETERS:
- calendarId: "{calendar_id}" (ALWAYS use this exact value)
- Duration: 2 hours default
- Time format: ISO 8601 with +04:00 timezone (Mauritius)
- Business hours: 11:00-22:00

CRITICAL RULES:
- NEVER fabricate event IDs or confirmations
- NEVER say "booking confirmed" without calling createEvent
- ALWAYS wait for createEvent response before confirming
- If createEvent fails, inform user of the error
- Payment is via AP2 protocol (agent-to-agent, not human-to-agent)
- WAIT for human approval before confirming payment

Example booking flow with payment:
Request: "Book for Friday 8pm, 6 people"
1. checkAvailability(calendarId="{calendar_id}",
   start="2025-10-17T20:00:00+04:00", end="2025-10-17T22:00:00+04:00")
2. If available: createEvent(calendarId="{calendar_id}",
   summary="Reservation - 6 guests", start="2025-10-17T20:00:00+04:00",
   end="2025-10-17T22:00:00+04:00")
3. request_payment(amount_usd=120.0, booking_id=eventId, description="Deposit for 6 guests")
4. Return: "Booking created! Event ID: [real-id]
           Payment required: $120 USDC
           Booking ID: [real-id]
           To complete, approve payment using: approve_payment(booking_id='[real-id]')" """,
    tools=[*gateway_tools, request_payment, check_payment_status, approve_payment],
)

host, port = "0.0.0.0", 9000  # noqa: S104 # Required for AgentCore container

# Create A2A server with runtime URL and serve_at_root=True
a2a_server = A2AServer(
    agent=strands_agent,
    http_url=runtime_url,
    serve_at_root=True,  # Serves locally at root (/) regardless of remote URL path
)

# Create FastAPI app with health check
app = FastAPI()


@app.get("/ping")
def ping():
    return {"status": "healthy", "agent": "La Bella Vita Restaurant Agent"}


# Mount A2A server at root
app.mount("/", a2a_server.to_fastapi_app())

if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)
