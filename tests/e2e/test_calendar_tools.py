"""E2E test for calendar tools via Gateway."""

import json
import os
from datetime import datetime, timedelta

import boto3
import pytest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


@pytest.fixture
def calendar_id():
    """Get calendar ID from environment."""
    return os.getenv(
        "GOOGLE_CALENDAR_ID",
        "f816bc2b3b70f58fcf66ac95ddb596707b9ece139b68ed226e161ddf4e57896f@group.calendar.google.com",
    )


@pytest.fixture
def lambda_client():
    """Create Lambda client."""
    return boto3.client("lambda", region_name="us-east-1")


@pytest.fixture
def google_calendar_service():
    """Create Google Calendar service."""
    token_path = os.path.expanduser("~/.google-calendar-token.json")
    if not os.path.exists(token_path):
        pytest.skip("Google Calendar token not found")

    with open(token_path) as f:
        token_data = json.load(f)

    creds = Credentials(
        token=token_data["token"],
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
    )

    return build("calendar", "v3", credentials=creds)


def test_check_availability_free_slot(lambda_client, calendar_id):
    """Test checkAvailability for a free time slot."""
    # Use a time far in the future to ensure it's free
    start_time = (datetime.now() + timedelta(days=365)).replace(
        hour=14, minute=0, second=0, microsecond=0
    )
    end_time = start_time + timedelta(hours=2)

    payload = {
        "action": "checkAvailability",
        "calendarId": calendar_id,
        "start": start_time.strftime("%Y-%m-%dT%H:%M:%S+04:00"),
        "end": end_time.strftime("%Y-%m-%dT%H:%M:%S+04:00"),
    }

    response = lambda_client.invoke(
        FunctionName="CalendarServiceStack-CalendarFunctionF225B08E-ydlKPqNVFCc8",
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )

    result = json.loads(response["Payload"].read())
    body = json.loads(result["body"])

    assert result["statusCode"] == 200
    assert body["success"] is True
    assert body["available"] is True


def test_create_and_delete_event(lambda_client, calendar_id, google_calendar_service):
    """Test createEvent and deleteEvent."""
    # Create event
    start_time = (datetime.now() + timedelta(days=30)).replace(
        hour=18, minute=0, second=0, microsecond=0
    )
    end_time = start_time + timedelta(hours=2)

    create_payload = {
        "action": "createEvent",
        "calendarId": calendar_id,
        "summary": "E2E Test Booking",
        "start": start_time.strftime("%Y-%m-%dT%H:%M:%S+04:00"),
        "end": end_time.strftime("%Y-%m-%dT%H:%M:%S+04:00"),
    }

    create_response = lambda_client.invoke(
        FunctionName="CalendarServiceStack-CalendarFunctionF225B08E-ydlKPqNVFCc8",
        InvocationType="RequestResponse",
        Payload=json.dumps(create_payload),
    )

    create_result = json.loads(create_response["Payload"].read())
    create_body = json.loads(create_result["body"])

    assert create_result["statusCode"] == 200
    assert create_body["success"] is True
    assert "eventId" in create_body

    event_id = create_body["eventId"]

    # Verify event exists in Google Calendar
    event = google_calendar_service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    assert event["summary"] == "E2E Test Booking"

    # Delete event
    delete_payload = {"action": "deleteEvent", "calendarId": calendar_id, "eventId": event_id}

    delete_response = lambda_client.invoke(
        FunctionName="CalendarServiceStack-CalendarFunctionF225B08E-ydlKPqNVFCc8",
        InvocationType="RequestResponse",
        Payload=json.dumps(delete_payload),
    )

    delete_result = json.loads(delete_response["Payload"].read())
    delete_body = json.loads(delete_result["body"])

    assert delete_result["statusCode"] == 200
    assert delete_body["success"] is True


def test_list_events(lambda_client, calendar_id):
    """Test listEvents."""
    payload = {"action": "listEvents", "calendarId": calendar_id, "maxResults": 10}

    response = lambda_client.invoke(
        FunctionName="CalendarServiceStack-CalendarFunctionF225B08E-ydlKPqNVFCc8",
        InvocationType="RequestResponse",
        Payload=json.dumps(payload),
    )

    result = json.loads(response["Payload"].read())
    body = json.loads(result["body"])

    assert result["statusCode"] == 200
    assert body["success"] is True
    assert "events" in body
    assert isinstance(body["events"], list)
