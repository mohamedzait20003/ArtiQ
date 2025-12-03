"""
SQS utility functions
Functions for interacting with AWS SQS queues
"""

import os
import json
import uuid
from typing import Dict, Any
from include import encrypt_artifact_id, get_sqs


def send_to_sqs(
    message_body: Dict[str, Any],
    queue_url: str = None,
    message_attributes: Dict[str, Dict[str, str]] = None
) -> bool:
    """
    Send a message to an SQS queue

    Args:
        message_body: Dictionary to send as JSON message body
        queue_url: SQS queue URL (uses env var if not provided)
        message_attributes: Optional message attributes for filtering

    Returns:
        True if message sent successfully, False otherwise
    """
    try:
        from include import get_sqs

        # Get SQS client
        sqs = get_sqs()

        # Get queue URL from environment if not provided
        if not queue_url:
            queue_url = os.environ.get('ARTIFACT_PROCESSING_QUEUE_URL')
            if not queue_url:
                print("⚠ Warning: No SQS queue URL configured")
                return False

        # Prepare message
        message_body_json = json.dumps(message_body)

        # Build send_message parameters
        send_params = {
            'QueueUrl': queue_url,
            'MessageBody': message_body_json
        }

        # Add message attributes if provided
        if message_attributes:
            send_params['MessageAttributes'] = message_attributes

        # Send message to SQS
        response = sqs.send_message(**send_params)

        print("✓ Sent message to SQS queue")
        print(f"  Message ID: {response.get('MessageId')}")
        return True

    except Exception as e:
        print(f"✗ Failed to send to SQS: {e}")
        return False


def send_artifact_to_sqs(
    artifact_id: str,
    artifact_type: str,
    encrypted: bool = True,
    queue_url: str = None
) -> bool:
    """
    Send artifact information to SQS for processing

    Args:
        artifact_id: The artifact ID
        artifact_type: Type of artifact (model, dataset, code)
        encrypted: Whether to encrypt the artifact ID
        queue_url: SQS queue URL (uses env var if not provided)

    Returns:
        True if message sent successfully, False otherwise
    """
    try:
        # Encrypt artifact ID if requested
        if encrypted:
            encrypted_id = encrypt_artifact_id(artifact_id)
            message_body = {
                'encrypted_artifact_id': encrypted_id,
                'artifact_type': artifact_type,
                'timestamp': str(uuid.uuid4())
            }
        else:
            message_body = {
                'artifact_id': artifact_id,
                'artifact_type': artifact_type,
                'timestamp': str(uuid.uuid4())
            }

        # Message attributes for filtering
        message_attributes = {
            'ArtifactType': {
                'StringValue': artifact_type,
                'DataType': 'String'
            }
        }

        # Send to SQS
        return send_to_sqs(message_body, queue_url, message_attributes)

    except Exception as e:
        print(f"✗ Failed to send artifact to SQS: {e}")
        return False


def receive_from_sqs(
    queue_url: str = None,
    max_messages: int = 1,
    wait_time_seconds: int = 0
) -> list:
    """
    Receive messages from an SQS queue

    Args:
        queue_url: SQS queue URL (uses env var if not provided)
        max_messages: Maximum number of messages to receive (1-10)
        wait_time_seconds: Long polling wait time (0-20 seconds)

    Returns:
        List of message dictionaries
    """
    try:
        # Get SQS client
        sqs = get_sqs()

        # Get queue URL from environment if not provided
        if not queue_url:
            queue_url = os.environ.get('ARTIFACT_PROCESSING_QUEUE_URL')
            if not queue_url:
                print("⚠ Warning: No SQS queue URL configured")
                return []

        # Receive messages
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=min(max_messages, 10),
            WaitTimeSeconds=wait_time_seconds,
            MessageAttributeNames=['All']
        )

        return response.get('Messages', [])

    except Exception as e:
        print(f"✗ Failed to receive from SQS: {e}")
        return []


def delete_from_sqs(receipt_handle: str, queue_url: str = None) -> bool:
    """
    Delete a message from an SQS queue

    Args:
        receipt_handle: Receipt handle from received message
        queue_url: SQS queue URL (uses env var if not provided)

    Returns:
        True if message deleted successfully, False otherwise
    """
    try:
        # Get SQS client
        sqs = get_sqs()

        # Get queue URL from environment if not provided
        if not queue_url:
            queue_url = os.environ.get('ARTIFACT_PROCESSING_QUEUE_URL')
            if not queue_url:
                print("⚠ Warning: No SQS queue URL configured")
                return False

        # Delete message
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

        print("✓ Deleted message from SQS queue")
        return True

    except Exception as e:
        print(f"✗ Failed to delete from SQS: {e}")
        return False
