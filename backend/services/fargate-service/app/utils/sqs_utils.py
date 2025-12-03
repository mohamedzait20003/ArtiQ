"""
SQS Utility Functions
Handles SQS message processing and queue operations
"""
import json
from include import decrypt_artifact_id, get_sqs_queue_url


def process_sqs_message(message: dict, sqs_client, process_callback) -> bool:
    """
    Process a single SQS message

    Args:
        message: The SQS message dictionary
        sqs_client: The SQS client instance
        process_callback: Function to call with decrypted artifact_id
                         Should return True on success

    Returns:
        True if message was processed successfully
    """
    try:
        receipt_handle = message.get('ReceiptHandle')
        body = message.get('Body')

        if not body:
            print("[FARGATE] Received message with no body")
            return False

        # Parse message body
        try:
            message_data = json.loads(body)
        except json.JSONDecodeError:
            print(f"[FARGATE] Invalid JSON in message body: {body}")
            return False

        # Extract encrypted artifact ID
        encrypted_id = message_data.get('encrypted_artifact_id')
        if not encrypted_id:
            print("[FARGATE] Message missing encrypted_artifact_id")
            return False

        print(f"[FARGATE] Received encrypted artifact ID: "
              f"{encrypted_id[:20]}...")

        # Decrypt artifact ID
        try:
            artifact_id = decrypt_artifact_id(encrypted_id)
            print(f"[FARGATE] Decrypted artifact ID: {artifact_id}")
        except Exception as e:
            print(f"[FARGATE] Failed to decrypt artifact ID: {e}")
            return False

        # Process the artifact using the callback
        success = process_callback(artifact_id)

        if success:
            # Delete message from queue
            queue_url = get_sqs_queue_url()
            sqs_client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )
            print("[FARGATE] Deleted message from queue")
            return True
        else:
            print("[FARGATE] Failed to process artifact, "
                  "message will be retried")
            return False

    except Exception as e:
        print(f"[FARGATE] Error processing SQS message: {e}")
        import traceback
        traceback.print_exc()
        return False
