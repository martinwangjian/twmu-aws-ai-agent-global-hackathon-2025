"""
AP2 (Agent Payment Protocol) + x402 Mock Payment Tool

Mock implementation of agent-native payment protocol using Coinbase x402 standard
for stablecoin (USDC) payments. For hackathon demonstration purposes.
"""

import json
import logging
import os
from datetime import UTC, datetime, timedelta
from typing import Any

import boto3
from strands.tools import tool

# Initialize S3 client for payment tracking
s3_client = boto3.client("s3")
PAYMENT_BUCKET = os.getenv("PAYMENT_TRACKING_BUCKET", "booking-agent-payments")

logger = logging.getLogger(__name__)


@tool
def request_payment(
    amount_usd: float,
    booking_id: str,
    description: str = "Restaurant booking deposit",
) -> dict[str, Any]:
    """
    Request payment via AP2 protocol with x402 stablecoins.

    Args:
        amount_usd: Payment amount in USD
        booking_id: Unique booking identifier
        description: Payment description

    Returns:
        Payment request details with x402 protocol information
    """
    # Generate payment request
    expires_at = datetime.now(UTC) + timedelta(minutes=15)
    payment_request = {
        "protocol": "AP2",
        "standard": "x402",
        "amount": amount_usd,
        "currency": "USDC",
        "recipient": "agent://booking-bot/payments",
        "booking_id": booking_id,
        "description": description,
        "payment_url": f"https://pay.coinbase.com/demo/{booking_id}",
        "expires_at": expires_at.isoformat(),
        "status": "pending",
        "created_at": datetime.now(UTC).isoformat(),
    }

    # Store payment request in S3
    try:
        s3_client.put_object(
            Bucket=PAYMENT_BUCKET,
            Key=f"payments/{booking_id}.json",
            Body=json.dumps(payment_request),
            ContentType="application/json",
        )
    except Exception as e:
        # Fallback: continue without storage
        logger.warning("Could not store payment request: %s", e)

    return {
        "success": True,
        "payment_request": payment_request,
        "message": f"💳 Payment request created: ${amount_usd} USDC\n\n"
        f"Pay via: {payment_request['payment_url']}\n"
        f"Expires in 15 minutes\n\n"
        f"Benefits:\n"
        f"✅ Instant settlement\n"
        f"✅ No currency conversion fees\n"
        f"✅ Secure blockchain transaction",
    }


@tool
def check_payment_status(booking_id: str) -> dict[str, Any]:
    """
    Check payment status for a booking.

    Args:
        booking_id: Unique booking identifier

    Returns:
        Payment status and transaction details
    """
    # Try to retrieve payment from S3
    try:
        response = s3_client.get_object(Bucket=PAYMENT_BUCKET, Key=f"payments/{booking_id}.json")
        payment_data = json.loads(response["Body"].read())

        return {
            "success": True,
            "booking_id": booking_id,
            "status": payment_data["status"],
            "amount": payment_data["amount"],
            "currency": payment_data["currency"],
            "tx_hash": payment_data.get("tx_hash"),
            "confirmed_at": payment_data.get("confirmed_at"),
            "message": (
                "✅ Payment confirmed!"
                if payment_data["status"] == "confirmed"
                else "⏳ Payment pending..."
            ),
        }

    except s3_client.exceptions.NoSuchKey:
        return {
            "success": False,
            "booking_id": booking_id,
            "status": "not_found",
            "message": "No payment request found for this booking",
        }
    except Exception as e:
        return {
            "success": False,
            "booking_id": booking_id,
            "status": "error",
            "message": f"Error checking payment status: {str(e)}",
        }


@tool
def approve_payment(booking_id: str) -> dict[str, Any]:
    """
    Approve a pending payment (human-in-the-loop).

    Args:
        booking_id: Booking ID to approve payment for

    Returns:
        Approval confirmation
    """
    try:
        # Get payment from S3
        response = s3_client.get_object(Bucket=PAYMENT_BUCKET, Key=f"payments/{booking_id}.json")
        payment_data = json.loads(response["Body"].read())

        if payment_data["status"] == "confirmed":
            return {
                "success": True,
                "message": f"Payment already confirmed for booking {booking_id}",
                "amount": payment_data["amount"],
                "currency": payment_data["currency"],
            }

        if payment_data["status"] == "cancelled":
            return {
                "success": False,
                "message": "Cannot approve cancelled payment",
            }

        # Update status to confirmed
        payment_data["status"] = "confirmed"
        payment_data["approved_at"] = datetime.now(UTC).isoformat()
        payment_data["tx_hash"] = f"0xdemo{booking_id[:8]}"

        # Save back to S3
        s3_client.put_object(
            Bucket=PAYMENT_BUCKET,
            Key=f"payments/{booking_id}.json",
            Body=json.dumps(payment_data),
            ContentType="application/json",
        )

        return {
            "success": True,
            "message": f"✅ Payment approved for booking {booking_id}",
            "amount": payment_data["amount"],
            "currency": payment_data["currency"],
            "tx_hash": payment_data["tx_hash"],
        }

    except s3_client.exceptions.NoSuchKey:
        return {
            "success": False,
            "message": f"No payment request found for booking {booking_id}",
        }
    except Exception as e:
        logger.warning("Error approving payment: %s", e)
        return {
            "success": False,
            "message": f"Error approving payment: {str(e)}",
        }


@tool
def cancel_payment(booking_id: str) -> dict[str, Any]:
    """
    Cancel a pending payment request.

    Args:
        booking_id: Unique booking identifier

    Returns:
        Cancellation status
    """
    try:
        # Retrieve payment
        response = s3_client.get_object(Bucket=PAYMENT_BUCKET, Key=f"payments/{booking_id}.json")
        payment_data = json.loads(response["Body"].read())

        if payment_data["status"] == "confirmed":
            return {
                "success": False,
                "message": "Cannot cancel confirmed payment. Please request refund.",
            }

        # Mark as cancelled
        payment_data["status"] = "cancelled"
        payment_data["cancelled_at"] = datetime.now(UTC).isoformat()

        s3_client.put_object(
            Bucket=PAYMENT_BUCKET,
            Key=f"payments/{booking_id}.json",
            Body=json.dumps(payment_data),
            ContentType="application/json",
        )

        return {
            "success": True,
            "booking_id": booking_id,
            "message": "Payment request cancelled successfully",
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error cancelling payment: {str(e)}",
        }
