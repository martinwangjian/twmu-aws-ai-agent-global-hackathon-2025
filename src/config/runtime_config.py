"""Runtime configuration from SSM Parameter Store with .env fallback."""

import os
from functools import lru_cache

import boto3


@lru_cache(maxsize=1)
def get_runtime_config() -> dict[str, str]:
    """Fetch config from SSM (cached) or .env fallback."""
    if os.getenv("LOCAL_DEV") == "true":
        calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
        model_id = os.getenv("BEDROCK_MODEL_ID")

        if not calendar_id:
            raise ValueError("GOOGLE_CALENDAR_ID must be set when LOCAL_DEV=true")
        if not model_id:
            raise ValueError("BEDROCK_MODEL_ID must be set when LOCAL_DEV=true")

        return {
            "calendar_id": calendar_id,
            "model_id": model_id,
            "kb_id": os.getenv("RESTAURANT_KB_ID") or "",
            "cognito_client_id": os.getenv("COGNITO_CLIENT_ID") or "",
            "cognito_discovery_url": os.getenv("COGNITO_DISCOVERY_URL") or "",
        }

    ssm = boto3.client("ssm", region_name="us-east-1")
    response = ssm.get_parameters_by_path(Path="/restaurant-booking/", WithDecryption=True)

    config = {}
    for param in response["Parameters"]:
        key = param["Name"].split("/")[-1].replace("-", "_")
        config[key] = param["Value"]

    if "calendar_id" not in config:
        raise ValueError("calendar_id not found in SSM parameters")
    if "model_id" not in config:
        raise ValueError("model_id not found in SSM parameters")

    return config


def get_calendar_id() -> str:
    """Get Google Calendar ID."""
    return get_runtime_config()["calendar_id"]


def get_model_id() -> str:
    """Get Bedrock model ID."""
    return get_runtime_config()["model_id"]


def get_kb_id() -> str:
    """Get Knowledge Base ID."""
    return get_runtime_config().get("kb_id", "")
