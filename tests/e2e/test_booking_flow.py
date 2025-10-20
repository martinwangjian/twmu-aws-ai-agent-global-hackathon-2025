"""E2E test for complete booking flow: discover → book → calendar event created.

This test validates the entire booking workflow and prevents regression of the
hallucination bug where agents confirmed bookings without creating calendar events.
"""

import contextlib
import json
import os
import re
from datetime import datetime, timedelta
from uuid import uuid4

import httpx
import pytest
from a2a.client import A2ACardResolver, ClientConfig, ClientFactory
from a2a.types import Message, Part, Role, TextPart
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Test configuration
A2A_AGENT_URL = os.getenv("A2A_AGENT_URL", "http://localhost:9000")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
TIMEOUT = 60


@pytest.fixture
def a2a_url(a2a_server):
    """Get A2A server URL."""
    return a2a_server


def create_message(*, role: Role = Role.user, text: str) -> Message:
    """Create A2A protocol message."""
    return Message(
        kind="message",
        role=role,
        parts=[Part(TextPart(kind="text", text=text))],
        message_id=uuid4().hex,
    )


@pytest.fixture
def calendar_service():
    """Google Calendar API client for verification."""
    if not SERVICE_ACCOUNT_JSON:
        pytest.skip("GOOGLE_SERVICE_ACCOUNT_JSON not configured")

    credentials_dict = json.loads(SERVICE_ACCOUNT_JSON)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_dict, scopes=["https://www.googleapis.com/auth/calendar"]
    )
    return build("calendar", "v3", credentials=credentials)


@pytest.fixture
def test_booking_time():
    """Generate a test booking time (tomorrow at 7pm)."""
    tomorrow = datetime.now()  # noqa: DTZ005 + timedelta(days=1)
    return tomorrow.replace(hour=19, minute=0, second=0, microsecond=0)


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.asyncio
async def test_complete_booking_flow_creates_real_calendar_event(
    a2a_url, calendar_service, test_booking_time, cleanup_calendar_events
):
    """Test that booking flow creates actual calendar event, not hallucination.

    Flow:
    1. Send booking request to A2A agent
    2. Agent should call checkAvailability
    3. Agent should call createEvent
    4. Verify event exists in Google Calendar
    5. Verify event ID matches response
    6. Cleanup: delete test event
    """
    # 1. Send booking request via A2A protocol
    async with httpx.AsyncClient(timeout=TIMEOUT) as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=a2a_url)
        agent_card = await resolver.get_agent_card()

        config = ClientConfig(httpx_client=httpx_client, streaming=False)
        factory = ClientFactory(config)
        client = factory.create(agent_card)

        msg = create_message(
            text=(
                f"Book La Bella Vita for {test_booking_time.strftime('%Y-%m-%d')} "
                f"at {test_booking_time.strftime('%I:%M %p')}, 2 people"
            )
        )

        response_text = ""
        async for event in client.send_message(msg):
            if isinstance(event, Message):
                for part in event.parts:
                    if hasattr(part, "text"):
                        response_text += part.text
            elif isinstance(event, tuple) and len(event) == 2:
                task, _ = event
                for artifact in task.artifacts:
                    for part in artifact.parts:
                        if hasattr(part.root, "text"):
                            response_text += part.root.text

    # 2. Extract event ID from response
    event_id_match = re.search(r"[a-z0-9]{26}", response_text)
    assert event_id_match, f"No event ID found in response: {response_text}"
    event_id = event_id_match.group(0)

    # 3. Verify event exists in Google Calendar
    try:
        event = calendar_service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()

        # 4. Verify event details
        assert event["id"] == event_id, "Event ID mismatch"
        assert "Reservation" in event.get("summary", ""), "Event summary missing"

        # Verify time matches request
        event_start = datetime.fromisoformat(event["start"]["dateTime"].replace("+04:00", ""))
        assert event_start.hour == test_booking_time.hour, "Booking time mismatch"

    finally:
        # 5. Cleanup: delete test event
        with contextlib.suppress(Exception):
            calendar_service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_booking_conflict_handling(
    a2a_url, calendar_service, test_booking_time, cleanup_calendar_events
):
    """Test agent handles booking conflicts correctly.

    Flow:
    1. Create a test event at target time
    2. Try to book same time
    3. Verify agent reports conflict
    4. Verify no duplicate event created
    5. Cleanup test event
    """
    # 1. Create blocking event
    start_time = test_booking_time.isoformat() + "+04:00"
    end_time = (test_booking_time + timedelta(hours=2)).isoformat() + "+04:00"

    blocking_event = {
        "summary": "Test Blocking Event",
        "start": {"dateTime": start_time},
        "end": {"dateTime": end_time},
    }

    created_event = (
        calendar_service.events().insert(calendarId=CALENDAR_ID, body=blocking_event).execute()
    )

    try:
        # 2. Try to book same time via A2A protocol
        async with httpx.AsyncClient(timeout=TIMEOUT) as httpx_client:
            resolver = A2ACardResolver(httpx_client=httpx_client, base_url=a2a_url)
            agent_card = await resolver.get_agent_card()

            config = ClientConfig(httpx_client=httpx_client, streaming=False)
            factory = ClientFactory(config)
            client = factory.create(agent_card)

            msg = create_message(
                text=(
                    f"Book La Bella Vita for {test_booking_time.strftime('%Y-%m-%d')} "
                    f"at {test_booking_time.strftime('%I:%M %p')}, 2 people"
                )
            )

            response_text = ""
            async for event in client.send_message(msg):
                if isinstance(event, Message):
                    for part in event.parts:
                        if hasattr(part, "text"):
                            response_text += part.text
                elif isinstance(event, tuple) and len(event) == 2:
                    task, _ = event
                    for artifact in task.artifacts:
                        for part in artifact.parts:
                            if hasattr(part.root, "text"):
                                response_text += part.root.text

        # 3. Verify conflict reported
        assert any(
            word in response_text.lower()
            for word in ["conflict", "unavailable", "not available", "booked"]
        ), f"Expected conflict message, got: {response_text}"

        # 4. Verify no duplicate event created
        events = (
            calendar_service.events()
            .list(
                calendarId=CALENDAR_ID,
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
            )
            .execute()
        )

        # Should only have the blocking event
        assert len(events.get("items", [])) == 1, "Duplicate event created!"

    finally:
        # 5. Cleanup
        calendar_service.events().delete(
            calendarId=CALENDAR_ID, eventId=created_event["id"]
        ).execute()
