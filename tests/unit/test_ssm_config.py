"""Tests for SSM Parameter Store configuration."""

import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def clear_config_cache():
    """Clear runtime_config cache before each test."""
    from src.config import runtime_config

    runtime_config.get_runtime_config.cache_clear()
    yield
    runtime_config.get_runtime_config.cache_clear()


def test_local_dev_with_env_vars(clear_config_cache):
    """Test LOCAL_DEV=true reads from environment variables."""
    with patch.dict(
        os.environ,
        {
            "LOCAL_DEV": "true",
            "GOOGLE_CALENDAR_ID": "test-calendar",
            "BEDROCK_MODEL_ID": "test-model",
        },
    ):
        from src.config.runtime_config import get_calendar_id, get_model_id

        assert get_calendar_id() == "test-calendar"
        assert get_model_id() == "test-model"


def test_local_dev_missing_calendar_id_fails(clear_config_cache):
    """Test LOCAL_DEV=true fails when GOOGLE_CALENDAR_ID missing."""
    with patch.dict(
        os.environ, {"LOCAL_DEV": "true", "BEDROCK_MODEL_ID": "test-model"}, clear=True
    ):
        from src.config.runtime_config import get_calendar_id

        with pytest.raises(ValueError, match="GOOGLE_CALENDAR_ID must be set"):
            get_calendar_id()


def test_local_dev_missing_model_id_fails(clear_config_cache):
    """Test LOCAL_DEV=true fails when BEDROCK_MODEL_ID missing."""
    with patch.dict(
        os.environ, {"LOCAL_DEV": "true", "GOOGLE_CALENDAR_ID": "test-calendar"}, clear=True
    ):
        from src.config.runtime_config import get_model_id

        with pytest.raises(ValueError, match="BEDROCK_MODEL_ID must be set"):
            get_model_id()


def test_production_ssm_fetch(clear_config_cache):
    """Test production mode fetches from SSM."""
    mock_ssm = MagicMock()
    mock_ssm.get_parameters_by_path.return_value = {
        "Parameters": [
            {"Name": "/restaurant-booking/calendar-id", "Value": "ssm-calendar"},
            {"Name": "/restaurant-booking/model-id", "Value": "ssm-model"},
        ]
    }

    with patch.dict(os.environ, {}, clear=True), patch("boto3.client", return_value=mock_ssm):
        from src.config.runtime_config import get_calendar_id, get_model_id

        assert get_calendar_id() == "ssm-calendar"
        assert get_model_id() == "ssm-model"

        mock_ssm.get_parameters_by_path.assert_called_once_with(
            Path="/restaurant-booking/", WithDecryption=True
        )


def test_production_missing_calendar_id_fails(clear_config_cache):
    """Test production mode fails when calendar_id not in SSM."""
    mock_ssm = MagicMock()
    mock_ssm.get_parameters_by_path.return_value = {
        "Parameters": [
            {"Name": "/restaurant-booking/model-id", "Value": "ssm-model"},
        ]
    }

    with patch.dict(os.environ, {}, clear=True), patch("boto3.client", return_value=mock_ssm):
        from src.config.runtime_config import get_calendar_id

        with pytest.raises(ValueError, match="calendar_id not found in SSM"):
            get_calendar_id()


def test_production_missing_model_id_fails(clear_config_cache):
    """Test production mode fails when model_id not in SSM."""
    mock_ssm = MagicMock()
    mock_ssm.get_parameters_by_path.return_value = {
        "Parameters": [
            {"Name": "/restaurant-booking/calendar-id", "Value": "ssm-calendar"},
        ]
    }

    with patch.dict(os.environ, {}, clear=True), patch("boto3.client", return_value=mock_ssm):
        from src.config.runtime_config import get_model_id

        with pytest.raises(ValueError, match="model_id not found in SSM"):
            get_model_id()


def test_config_caching(clear_config_cache):
    """Test that config is cached and SSM is only called once."""
    mock_ssm = MagicMock()
    mock_ssm.get_parameters_by_path.return_value = {
        "Parameters": [
            {"Name": "/restaurant-booking/calendar-id", "Value": "ssm-calendar"},
            {"Name": "/restaurant-booking/model-id", "Value": "ssm-model"},
        ]
    }

    with patch.dict(os.environ, {}, clear=True), patch("boto3.client", return_value=mock_ssm):
        from src.config.runtime_config import get_calendar_id, get_model_id

        # Call multiple times
        get_calendar_id()
        get_model_id()
        get_calendar_id()

        # SSM should only be called once due to caching
        assert mock_ssm.get_parameters_by_path.call_count == 1
