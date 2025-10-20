"""Tests for AP2 + x402 payment tools."""

import json
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from src.agents.tools.payment_tool import (
    cancel_payment,
    check_payment_status,
    request_payment,
)


@pytest.fixture
def mock_s3():
    """Mock S3 client."""
    with patch("src.agents.tools.payment_tool.s3_client") as mock:
        yield mock


def test_request_payment_success(mock_s3):
    """Test successful payment request creation."""
    result = request_payment(amount_usd=10.0, booking_id="test-123", description="Test booking")

    assert result["success"] is True
    assert result["payment_request"]["amount"] == 10.0
    assert result["payment_request"]["currency"] == "USDC"
    assert result["payment_request"]["protocol"] == "AP2"
    assert result["payment_request"]["standard"] == "x402"
    assert result["payment_request"]["booking_id"] == "test-123"
    assert "pay.coinbase.com" in result["payment_request"]["payment_url"]
    assert result["payment_request"]["status"] == "pending"

    # Verify S3 storage was called
    mock_s3.put_object.assert_called_once()


def test_request_payment_s3_failure(mock_s3):
    """Test payment request continues even if S3 fails."""
    mock_s3.put_object.side_effect = Exception("S3 error")

    result = request_payment(amount_usd=10.0, booking_id="test-456")

    # Should still return success (graceful degradation)
    assert result["success"] is True
    assert result["payment_request"]["amount"] == 10.0


def test_check_payment_status_not_found(mock_s3):
    """Test checking status for non-existent payment."""
    mock_s3.get_object.side_effect = mock_s3.exceptions.NoSuchKey("Not found")

    result = check_payment_status(booking_id="nonexistent")

    assert result["success"] is False
    assert result["status"] == "not_found"


def test_check_payment_status_pending(mock_s3):
    """Test checking status for pending payment (< 30 seconds old)."""
    payment_data = {
        "protocol": "AP2",
        "amount": 10.0,
        "currency": "USDC",
        "booking_id": "test-789",
        "status": "pending",
        "created_at": datetime.now(UTC).isoformat(),
    }

    mock_response = MagicMock()
    mock_response["Body"].read.return_value = json.dumps(payment_data).encode()
    mock_s3.get_object.return_value = mock_response

    result = check_payment_status(booking_id="test-789")

    assert result["success"] is True
    assert result["status"] == "pending"
    assert result["amount"] == 10.0


def test_check_payment_status_auto_confirm(mock_s3):
    """Test auto-confirmation after 30 seconds."""
    # Create payment older than 30 seconds
    old_time = datetime.now(UTC)
    old_time = old_time.replace(second=old_time.second - 35)

    payment_data = {
        "protocol": "AP2",
        "amount": 10.0,
        "currency": "USDC",
        "booking_id": "test-auto",
        "status": "pending",
        "created_at": old_time.isoformat(),
    }

    mock_response = MagicMock()
    mock_response["Body"].read.return_value = json.dumps(payment_data).encode()
    mock_s3.get_object.return_value = mock_response

    result = check_payment_status(booking_id="test-auto")

    assert result["success"] is True
    assert result["status"] == "confirmed"
    assert "tx_hash" in result
    assert result["tx_hash"].startswith("0xdemo")

    # Verify S3 was updated with confirmed status
    mock_s3.put_object.assert_called_once()


def test_cancel_payment_success(mock_s3):
    """Test successful payment cancellation."""
    payment_data = {
        "protocol": "AP2",
        "amount": 10.0,
        "booking_id": "test-cancel",
        "status": "pending",
        "created_at": datetime.now(UTC).isoformat(),
    }

    mock_response = MagicMock()
    mock_response["Body"].read.return_value = json.dumps(payment_data).encode()
    mock_s3.get_object.return_value = mock_response

    result = cancel_payment(booking_id="test-cancel")

    assert result["success"] is True
    assert "cancelled successfully" in result["message"]

    # Verify S3 was updated
    mock_s3.put_object.assert_called_once()


def test_cancel_payment_already_confirmed(mock_s3):
    """Test cannot cancel confirmed payment."""
    payment_data = {
        "protocol": "AP2",
        "amount": 10.0,
        "booking_id": "test-confirmed",
        "status": "confirmed",
        "created_at": datetime.now(UTC).isoformat(),
    }

    mock_response = MagicMock()
    mock_response["Body"].read.return_value = json.dumps(payment_data).encode()
    mock_s3.get_object.return_value = mock_response

    result = cancel_payment(booking_id="test-confirmed")

    assert result["success"] is False
    assert "Cannot cancel confirmed payment" in result["message"]


def test_payment_expiration_format():
    """Test payment expiration is 15 minutes from creation."""
    result = request_payment(amount_usd=10.0, booking_id="test-expiry")

    created = datetime.fromisoformat(result["payment_request"]["created_at"])
    expires = datetime.fromisoformat(result["payment_request"]["expires_at"])

    diff_minutes = (expires - created).total_seconds() / 60
    assert 14.9 < diff_minutes < 15.1  # Allow small floating point variance
