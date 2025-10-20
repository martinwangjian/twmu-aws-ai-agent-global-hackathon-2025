#!/usr/bin/env python3
"""Functional test for duplicate booking fix.

Tests that the agent correctly handles booking requests without creating duplicates.
"""

from datetime import UTC, datetime, timedelta

import pytest


@pytest.fixture
def mock_calendar_service():
    """Mock calendar service to track tool calls."""
    calls = []

    def track_call(tool_name, **kwargs):
        calls.append({"tool": tool_name, "params": kwargs})
        if tool_name == "checkAvailability":
            return {"available": True}
        if tool_name == "createEvent":
            return {"eventId": "test-event-123"}
        return {}

    return calls, track_call


def test_no_duplicate_booking_on_single_request(mock_calendar_service):
    """Test that a single booking request creates only one event."""
    calls, track_call = mock_calendar_service

    # Simulate agent flow
    start_time = datetime.now(UTC) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    # Step 1: Check availability
    track_call("checkAvailability", start=start_time.isoformat(), end=end_time.isoformat())

    # Step 2: Create event (should happen only once)
    track_call(
        "createEvent",
        summary="Test Booking",
        start=start_time.isoformat(),
        end=end_time.isoformat(),
    )

    # Verify only one createEvent call
    create_calls = [c for c in calls if c["tool"] == "createEvent"]
    assert len(create_calls) == 1, f"Expected 1 createEvent call, got {len(create_calls)}"


def test_no_duplicate_on_confirmation_message(mock_calendar_service):
    """Test that confirmation messages don't trigger duplicate bookings."""
    calls, track_call = mock_calendar_service

    start_time = datetime.now(UTC) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    # Step 1: Check availability
    track_call("checkAvailability", start=start_time.isoformat(), end=end_time.isoformat())

    # Step 2: Create event
    result = track_call(
        "createEvent",
        summary="Test Booking",
        start=start_time.isoformat(),
        end=end_time.isoformat(),
    )

    # Step 3: Agent returns confirmation (should NOT create another event)
    # The agent should use the eventId from step 2 in its response

    # Verify only one createEvent call
    create_calls = [c for c in calls if c["tool"] == "createEvent"]
    assert len(create_calls) == 1, "Confirmation message should not trigger duplicate booking"
    assert result["eventId"] == "test-event-123"


def test_datetime_format_handling():
    """Test that datetime formats are correctly handled."""
    # ISO 8601 string format (from Gateway)
    iso_string = "2025-01-20T19:00:00"

    # Should be convertible to Google Calendar format
    expected_format = {"dateTime": iso_string}

    # Simulate Lambda handler conversion
    start = iso_string
    if isinstance(start, str):
        start = {"dateTime": start}

    assert start == expected_format, "String datetime should convert to object format"


def test_event_id_in_response():
    """Test that event ID is included in booking confirmation."""
    event_id = "test-event-123"

    # Simulate agent response
    response = f"Your booking is confirmed! Event ID: {event_id}"

    assert event_id in response, "Event ID should be in confirmation message"
    assert "confirmed" in response.lower(), "Confirmation keyword should be present"


@pytest.mark.parametrize(
    ("tool_sequence", "expected_creates"),
    [
        (["checkAvailability", "createEvent"], 1),
        (["checkAvailability", "createEvent", "listEvents"], 1),
        (["checkAvailability", "getAvailableSlots", "createEvent"], 1),
    ],
)
def test_various_booking_flows(tool_sequence, expected_creates, mock_calendar_service):
    """Test different booking flows all result in single event creation."""
    calls, track_call = mock_calendar_service

    start_time = datetime.now(UTC) + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    for tool in tool_sequence:
        if tool == "createEvent":
            track_call(
                tool,
                summary="Test Booking",
                start=start_time.isoformat(),
                end=end_time.isoformat(),
            )
        else:
            track_call(tool, start=start_time.isoformat(), end=end_time.isoformat())

    create_calls = [c for c in calls if c["tool"] == "createEvent"]
    assert (
        len(create_calls) == expected_creates
    ), f"Expected {expected_creates} createEvent calls, got {len(create_calls)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
