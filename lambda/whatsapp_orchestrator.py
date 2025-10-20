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

"""Lambda orchestrator for WhatsApp messages."""

import json
import logging
import os

import boto3
from aws_xray_sdk.core import patch_all, xray_recorder

# Patch AWS SDK for X-Ray tracing
patch_all()

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

agentcore = boto3.client("bedrock-agentcore")
socialmessaging = boto3.client("socialmessaging")


@xray_recorder.capture("mark_message_as_read")
def mark_message_as_read(phone_number_id: str, message_id: str) -> None:
    """Mark WhatsApp message as read."""
    try:
        message_payload = {
            "messaging_product": "whatsapp",
            "message_id": message_id,
            "status": "read",
        }

        socialmessaging.send_whatsapp_message(
            originationPhoneNumberId=phone_number_id,
            message=json.dumps(message_payload).encode("utf-8"),
            metaApiVersion="v19.0",
        )
        logger.info(f"Marked message as read: {message_id}")
    except Exception as e:
        logger.error(f"Error marking message as read: {e}", exc_info=True)


@xray_recorder.capture("send_typing_indicator")
def send_typing_indicator(phone_number_id: str, user_phone: str, typing: bool = True) -> None:
    """Send typing indicator to WhatsApp user.

    Args:
        phone_number_id: WhatsApp phone number ID
        user_phone: User's phone number
        typing: True to show typing, False to stop
    """
    try:
        message_payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": user_phone,
            "type": "reaction" if not typing else "text",
        }

        # WhatsApp typing indicator is sent via the typing action
        if typing:
            # Send typing action via Cloud API
            message_payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": user_phone,
                "typing": "on",
            }

        socialmessaging.send_whatsapp_message(
            originationPhoneNumberId=phone_number_id,
            message=json.dumps(message_payload).encode("utf-8"),
            metaApiVersion="v19.0",
        )
        logger.info(f"Sent typing indicator ({'on' if typing else 'off'}) to {user_phone}")
    except Exception as e:
        logger.error(f"Error sending typing indicator: {e}", exc_info=True)


@xray_recorder.capture("send_whatsapp_reply")
def send_whatsapp_reply(phone_number_id: str, user_phone: str, message: str) -> str:
    """Send WhatsApp reply message."""
    message_payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": user_phone,
        "type": "text",
        "text": {"body": message},
    }

    logger.debug(f"Sending to phone: {user_phone}")
    logger.debug(f"Message payload: {json.dumps(message_payload)}")

    response = socialmessaging.send_whatsapp_message(
        originationPhoneNumberId=phone_number_id,
        message=json.dumps(message_payload).encode("utf-8"),
        metaApiVersion="v19.0",
    )

    message_id = response.get("messageId", "")
    logger.info(f"WhatsApp reply sent: {message_id}")
    return str(message_id)


def generate_session_id(phone_number: str) -> str:
    """Generate session ID for conversation continuity.

    Uses phone number + date for daily session continuity.
    Session ID must be 33-256 characters and match [a-zA-Z0-9][a-zA-Z0-9-_]*
    """
    import hashlib
    from datetime import datetime

    # Remove + prefix for validation compliance
    clean_phone = phone_number.lstrip("+")
    date = datetime.utcnow().strftime("%Y%m%d")
    base = f"whatsapp-{clean_phone}-{date}"
    hash_suffix = hashlib.sha256(base.encode()).hexdigest()[:10]
    return f"{base}-{hash_suffix}"


@xray_recorder.capture("invoke_agentcore")
def invoke_agentcore(runtime_arn: str, session_id: str, prompt: str, actor_id: str) -> str:
    """Invoke AgentCore with user prompt and memory support."""
    params = {
        "agentRuntimeArn": runtime_arn,
        "runtimeSessionId": session_id,
        "payload": json.dumps(
            {
                "prompt": prompt,
                "session_id": session_id,
                "actor_id": actor_id,
            }
        ),
    }

    logger.info(f"Actor: {actor_id}, Session: {session_id}")

    response = agentcore.invoke_agent_runtime(**params)
    result = json.loads(response["response"].read())
    return str(result.get("result", "Sorry, I couldn't process that."))


def handler(event, context):  # noqa: PLR0912, PLR0915
    """Handle WhatsApp messages from SNS.

    Args:
        event: SNS event with WhatsApp message
        context: Lambda context

    Returns:
        Success response
    """
    runtime_arn = os.environ["AGENTCORE_RUNTIME_ARN"]
    phone_number_id = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")

    logger.debug(f"Full event: {json.dumps(event)}")

    for record in event["Records"]:
        # Parse SNS message
        sns_message = json.loads(record["Sns"]["Message"])
        logger.debug(f"SNS Message: {json.dumps(sns_message)}")

        # Parse WhatsApp webhook entry
        if "whatsAppWebhookEntry" not in sns_message:
            logger.warning("No whatsAppWebhookEntry in SNS message")
            continue

        whatsapp_data = json.loads(sns_message["whatsAppWebhookEntry"])
        logger.debug(f"WhatsApp data: {json.dumps(whatsapp_data)}")

        # Extract phone number ARN from context
        if not phone_number_id:
            phone_numbers = sns_message.get("context", {}).get("MetaPhoneNumberIds", [])
            if phone_numbers:
                phone_number_id = phone_numbers[0].get("arn")
                logger.info(f"Using phone number ARN: {phone_number_id}")

        # Extract message from webhook structure
        try:
            changes = whatsapp_data.get("changes", [])
            if not changes:
                logger.debug("No changes in webhook")
                continue

            value = changes[0].get("value", {})

            # Check if this is a status update (not a message)
            if "statuses" in value:
                logger.debug("Status update received, skipping")
                continue

            messages = value.get("messages", [])
            if not messages:
                logger.debug("No messages found")
                continue

            message = messages[0]
            user_phone = message.get("from", "unknown")
            # Add + prefix if not present
            if not user_phone.startswith("+"):
                user_phone = f"+{user_phone}"

            user_message = message.get("text", {}).get("body", "")
            message_id = message.get("id", "")

            # Get sender name
            contacts = value.get("contacts", [])
            sender_name = (
                contacts[0].get("profile", {}).get("name", "Unknown") if contacts else "Unknown"
            )

            logger.info(f"WhatsApp from {sender_name} ({user_phone}): {user_message}")

            if not user_message:
                logger.warning("Empty message body")
                continue

            # Mark message as read immediately
            if phone_number_id and message_id:
                mark_message_as_read(phone_number_id, message_id)

            # Show typing indicator while processing
            if phone_number_id:
                send_typing_indicator(phone_number_id, user_phone, typing=True)

            # Invoke AgentCore with actor_id and session_id
            # Sanitize actor_id: remove + prefix for memory API compliance
            actor_id = user_phone.lstrip("+")  # Remove + prefix
            session_id = generate_session_id(user_phone)
            logger.info(f"Actor: {actor_id}, Session: {session_id}")

            ai_reply = invoke_agentcore(runtime_arn, session_id, user_message, actor_id)
            logger.info(f"AI reply: {ai_reply}")

            # Send reply via WhatsApp (typing indicator stops automatically when message sent)
            if phone_number_id:
                try:
                    send_whatsapp_reply(phone_number_id, user_phone, ai_reply)
                except Exception as e:
                    logger.error(f"Error sending WhatsApp reply: {e}", exc_info=True)
            else:
                logger.error("No phone number ID configured")

        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {e}", exc_info=True)

    return {"statusCode": 200, "body": json.dumps("Processed")}


# Updated: Thu Oct  9 20:40:46 CEST 2025
