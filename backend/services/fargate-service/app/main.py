"""
Fargate Service - SQS Message Processor
Listens to SQS queue for artifact processing requests
"""
import os
import sys
import time
import signal
from app.utils.sqs_utils import process_sqs_message
from app.models.Artifact_Model import Artifact_Model
from include import get_sqs, get_sqs_queue_url, AWSServices

os.environ.setdefault("AWS_REGION", "us-east-2")
AWSServices.initialize(region=os.environ.get("AWS_REGION"))

# Global flag for graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_requested
    print(f"\n[FARGATE] Received signal {signum}. "
          f"Initiating graceful shutdown...")
    shutdown_requested = True


def get_artifact_from_db(artifact_id: str):
    """
    Retrieve artifact from database by ID

    Args:
        artifact_id: The artifact ID to retrieve

    Returns:
        Artifact object or None if not found
    """
    try:
        artifact = Artifact_Model.get(
            {'id': artifact_id},
            load_s3_data=False
        )
        return artifact
    except Exception as e:
        print(f"[FARGATE] Error retrieving artifact {artifact_id}: {e}")
        return None


def process_artifact(artifact_id: str) -> bool:
    """
    Process an artifact by creating a pipeline

    Args:
        artifact_id: The decrypted artifact ID

    Returns:
        True if processing succeeded, False otherwise
    """
    print(f"[FARGATE] Processing artifact: {artifact_id}")

    try:
        # Retrieve artifact from database
        artifact = get_artifact_from_db(artifact_id)

        if not artifact:
            print(f"[FARGATE] Artifact {artifact_id} not found in database")
            return False

        print(f"[FARGATE] Found artifact: {artifact.name} "
              f"(type: {artifact.artifact_type})")
        print(f"[FARGATE] Source URL: {artifact.source_url}")

        # TODO: Implement pipeline creation logic here
        # This will depend on the artifact type and requirements
        # For now, just log the artifact details

        print(f"[FARGATE] Successfully processed artifact {artifact_id}")
        return True

    except Exception as e:
        print(f"[FARGATE] Error processing artifact {artifact_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


def poll_sqs_queue(sqs_client, queue_url: str):
    """
    Poll SQS queue for messages

    Args:
        sqs_client: The SQS client instance
        queue_url: The SQS queue URL
    """
    print(f"[FARGATE] Starting to poll queue: {queue_url}")

    while not shutdown_requested:
        try:
            # Receive messages from queue
            response = sqs_client.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,  # Process one at a time
                WaitTimeSeconds=20,  # Long polling
                MessageAttributeNames=['All']
            )

            messages = response.get('Messages', [])

            if not messages:
                print("[FARGATE] No messages in queue, continuing to poll...")
                continue

            print(f"[FARGATE] Received {len(messages)} message(s)")

            for message in messages:
                process_sqs_message(message, sqs_client, process_artifact)

        except Exception as e:
            print(f"[FARGATE] Error polling SQS queue: {e}")
            import traceback
            traceback.print_exc()
            # Wait before retrying
            time.sleep(5)

    print("[FARGATE] Stopped polling queue")


def main():
    """Main entry point for the Fargate service"""
    print("[FARGATE] Artifact Processing Service Starting...")

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Get configuration from environment
    queue_url = get_sqs_queue_url()
    encryption_key = os.environ.get('ARTIFACT_ENCRYPTION_KEY')

    if not queue_url:
        print("[FARGATE] ERROR: ARTIFACT_PROCESSING_QUEUE_URL "
              "not set in environment")
        sys.exit(1)

    if not encryption_key:
        print("[FARGATE] ERROR: ARTIFACT_ENCRYPTION_KEY "
              "not set in environment")
        sys.exit(1)

    print(f"[FARGATE] Queue URL: {queue_url}")
    print(f"[FARGATE] Encryption key configured: "
          f"{encryption_key[:10]}...")

    # Initialize SQS client
    try:
        sqs_client = get_sqs()
        print("[FARGATE] SQS client initialized successfully")
    except Exception as e:
        print(f"[FARGATE] ERROR: Failed to initialize SQS client: {e}")
        sys.exit(1)

    # Start polling the queue
    poll_sqs_queue(sqs_client, queue_url)

    print("[FARGATE] Service shutting down gracefully")
    sys.exit(0)


if __name__ == "__main__":
    main()
