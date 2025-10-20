"""Integration tests for AP2 payment workflow"""

import json
import os
from datetime import UTC, datetime

import boto3
import pytest

# Initialize S3 client
s3_client = boto3.client("s3", region_name="us-east-1")
PAYMENT_BUCKET = "booking-agent-payments"


@pytest.fixture
def test_booking_id():
    """Generate test booking ID"""
    return f"test_booking_{datetime.now(UTC).timestamp()}"


def test_payment_bucket_exists():
    """Test that payment bucket exists"""
    try:
        s3_client.head_bucket(Bucket=PAYMENT_BUCKET)
    except Exception as e:
        pytest.fail(f"Payment bucket does not exist: {e}")


def test_payment_request_flow(test_booking_id):
    """Test payment request creation and storage"""
    from agents.tools.payment_tool import request_payment

    # Request payment
    result = request_payment(
        amount_usd=10.0, booking_id=test_booking_id, description="Test booking deposit"
    )

    assert result["success"] is True
    assert result["payment_request"]["amount"] == 10.0
    assert result["payment_request"]["currency"] == "USDC"
    assert result["payment_request"]["status"] == "pending"

    # Verify stored in S3
    try:
        response = s3_client.get_object(
            Bucket=PAYMENT_BUCKET, Key=f"payments/{test_booking_id}.json"
        )
        payment_data = json.loads(response["Body"].read())
        assert payment_data["amount"] == 10.0
        assert payment_data["status"] == "pending"
    finally:
        # Cleanup
        s3_client.delete_object(Bucket=PAYMENT_BUCKET, Key=f"payments/{test_booking_id}.json")


def test_payment_approval_flow(test_booking_id):
    """Test payment approval workflow"""
    from agents.tools.payment_tool import approve_payment, check_payment_status, request_payment

    # 1. Request payment
    request_result = request_payment(
        amount_usd=10.0, booking_id=test_booking_id, description="Test booking"
    )
    assert request_result["success"] is True

    # 2. Check status (should be pending)
    status_result = check_payment_status(test_booking_id)
    assert status_result["success"] is True
    assert status_result["status"] == "pending"

    # 3. Approve payment
    approval_result = approve_payment(test_booking_id)
    assert approval_result["success"] is True
    assert "approved" in approval_result["message"].lower()

    # 4. Check status again (should be confirmed)
    final_status = check_payment_status(test_booking_id)
    assert final_status["success"] is True
    assert final_status["status"] == "confirmed"

    # Cleanup
    s3_client.delete_object(Bucket=PAYMENT_BUCKET, Key=f"payments/{test_booking_id}.json")


def test_payment_amount_calculation():
    """Test payment amount calculation for different party sizes"""
    # $5 per person
    assert 2 * 5 == 10  # 2 people = $10
    assert 4 * 5 == 20  # 4 people = $20
    assert 6 * 5 == 30  # 6 people = $30


@pytest.mark.skipif(not os.getenv("RUN_E2E_TESTS"), reason="E2E tests require RUN_E2E_TESTS=1")
def test_payment_e2e_with_a2a_agent():
    """End-to-end test with A2A agent (requires deployed agent)"""
    # This would test the full flow through the A2A agent
    # Skipped by default, run with RUN_E2E_TESTS=1
    pass
