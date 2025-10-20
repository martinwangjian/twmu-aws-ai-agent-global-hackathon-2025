# Copyright (C) 2025 Teamwork Mauritius
#
# This file is part of AWS AI Agent Global Hackathon 2025 submission.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Pytest configuration for BDD tests."""

import json
import os
import subprocess
import time
import urllib.request
from datetime import datetime
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Load .env file for all tests
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


@pytest.fixture(scope="session")
def a2a_server():
    """Start A2A server for e2e tests."""
    import httpx

    project_root = Path(__file__).parent.parent

    # Load .env and pass all vars to subprocess
    load_dotenv(project_root / ".env", override=True)
    env = os.environ.copy()
    env["LOCAL_DEV"] = "true"

    # Ensure required env vars are set
    required_vars = [
        "GOOGLE_CALENDAR_ID",
        "BEDROCK_MODEL_ID",
        "RESTAURANT_KB_ID",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
    ]
    for var in required_vars:
        if var not in env:
            pytest.skip(f"Missing required environment variable: {var}")

    log_file = project_root / "a2a_server_test.log"
    with open(log_file, "w") as f:
        process = subprocess.Popen(  # noqa: S603, S607
            ["uv", "run", "python", "src/agents/agentcore_a2a_server.py"],  # noqa: S607
            cwd=project_root,
            env=env,
            stdout=f,
            stderr=subprocess.STDOUT,
        )

    # Wait for server to be ready
    url = "http://localhost:9000/.well-known/agent-card.json"
    for _ in range(30):  # Try for 30 seconds
        time.sleep(1)
        if process.poll() is not None:
            with open(log_file) as f:
                pytest.fail(f"A2A server failed to start:\n{f.read()}")
        try:
            with httpx.Client() as client:
                response = client.get(url, timeout=1)
                if response.status_code == 200:
                    break
        except Exception:  # noqa: S112
            continue
    else:
        process.terminate()
        with open(log_file) as f:
            pytest.fail(f"A2A server did not start in time:\n{f.read()}")

    yield "http://localhost:9000"

    process.terminate()
    process.wait(timeout=5)


@pytest.fixture
def cleanup_calendar_events():
    """Clean up test calendar events after each test."""
    yield

    # Cleanup after test
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID")

    if not service_account_json or not calendar_id:
        return

    credentials_dict = json.loads(service_account_json)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_dict, scopes=["https://www.googleapis.com/auth/calendar"]
    )
    calendar_service = build("calendar", "v3", credentials=credentials)

    # Delete events from tomorrow
    tomorrow = datetime.now()  # noqa: DTZ005 + timedelta(days=1)
    time_min = tomorrow.replace(hour=0, minute=0, second=0).isoformat() + "Z"
    time_max = tomorrow.replace(hour=23, minute=59, second=59).isoformat() + "Z"

    events = (
        calendar_service.events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
        )
        .execute()
    )

    for event in events.get("items", []):
        calendar_service.events().delete(calendarId=calendar_id, eventId=event["id"]).execute()


@pytest.fixture
def context():
    """Shared context for test scenarios."""
    return {}


@pytest.fixture
def cognito_token():
    """Get Cognito OAuth token for A2A agent access."""
    body = json.dumps(
        {
            "AuthFlow": "USER_PASSWORD_AUTH",
            "ClientId": "qli2ric7jaush0pjstogu4vua",
            "AuthParameters": {"USERNAME": "a2a-client", "PASSWORD": "A2AClient2025!"},
        }
    ).encode()

    req = urllib.request.Request(
        "https://cognito-idp.us-east-1.amazonaws.com/",
        data=body,
        headers={
            "Content-Type": "application/x-amz-json-1.1",
            "X-Amz-Target": "AWSCognitoIdentityProviderService.InitiateAuth",
        },
    )

    with urllib.request.urlopen(req) as response:  # noqa: S310
        result = json.loads(response.read())
        return result["AuthenticationResult"]["AccessToken"]


@pytest.fixture
def a2a_agent_url():
    """Get A2A agent URL from environment."""
    return os.getenv(
        "A2A_AGENT_URL",
        "https://bedrock-agentcore.us-east-1.amazonaws.com/runtimes/"
        "arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A<YOUR_AWS_ACCOUNT_ID>%3Aruntime%2F"
        "<YOUR_AGENTCORE_RUNTIME_ID>",
    )


@pytest.fixture
def a2a_invocation_url(a2a_agent_url):
    """Get A2A agent invocation endpoint."""
    return f"{a2a_agent_url}/invocations"
