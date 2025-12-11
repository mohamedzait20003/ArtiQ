"""
Fargate Service - Artifact Processor
Processes artifacts using evaluation pipelines
Designed to be invoked as an ephemeral task from Lambda
"""
import os
import sys
import json
from include import AWSServices, Pipeline, Parallel
from app.utils.encryption import decrypt_artifact_id
from app.utils.artifact import get_artifact_from_db
from app.jobs import (
    validate_artifact_step, fetch_metadata_step,
    aggregate_scores_step, save_ratings_step,
    evaluate_bus_factor, evaluate_license,
    evaluate_performance, evaluate_rampup, evaluate_size,
    evaluate_availability, evaluate_code_quality,
    evaluate_dataset_quality
)


os.environ.setdefault("AWS_REGION", "us-east-2")
AWSServices.initialize(region=os.environ.get("AWS_REGION"))


def process_artifact(encrypted_artifact_id: str) -> dict:
    """
    Process an artifact by creating and running evaluation pipeline

    Args:
        encrypted_artifact_id: The encrypted artifact ID

    Returns:
        dict: Processing result with status and details
    """
    print(f"[FARGATE] Processing encrypted artifact ID: "
          f"{encrypted_artifact_id}")

    try:
        # Decrypt the artifact ID
        artifact_id = decrypt_artifact_id(encrypted_artifact_id)
        print(f"[FARGATE] Decrypted artifact ID: {artifact_id}")

        # Retrieve artifact from database
        artifact = get_artifact_from_db(artifact_id)

        if not artifact:
            print(f"[FARGATE] Artifact {artifact_id} not found in database")
            return {
                'success': False,
                'artifact_id': artifact_id,
                'error': 'Artifact not found'
            }

        print(f"[FARGATE] Found artifact: {artifact.name} "
              f"(type: {artifact.artifact_type})")
        print(f"[FARGATE] Source URL: {artifact.source_url}")

        # Execute the evaluation pipeline
        try:
            result = Pipeline(
                validate_artifact_step,
                fetch_metadata_step,
                Parallel(
                    evaluate_bus_factor,
                    evaluate_performance,
                    evaluate_rampup,
                    evaluate_size,
                    evaluate_license,
                    evaluate_availability,
                    evaluate_code_quality,
                    evaluate_dataset_quality,
                    max_workers=8
                ),
                aggregate_scores_step,
                save_ratings_step
            ).start(artifact)

            print("[FARGATE] Pipeline completed successfully")
            print(f"[FARGATE] Final scores: {result.get('scores', {})}")

            return {
                'success': True,
                'artifact_id': artifact_id,
                'artifact_name': artifact.name,
                'artifact_type': artifact.artifact_type,
                'ratings': result.get('scores', {}),
                'net_score': result.get('net_score', 0.0)
            }

        except Exception as pipeline_error:
            print(f"[FARGATE] Pipeline execution failed: {pipeline_error}")
            import traceback
            traceback.print_exc()
            raise

    except Exception as e:
        print(f"[FARGATE] Error processing artifact: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'encrypted_artifact_id': encrypted_artifact_id,
            'error': str(e)
        }


def handler(event, context=None):
    """
    Lambda-compatible handler for Fargate task invocation

    This function is designed to be called when the Fargate container
    starts, processing the encrypted artifact_id passed via command line
    or event.

    Args:
        event: Event data (can be dict or string encrypted artifact_id)
        context: Lambda context (optional, for compatibility)

    Returns:
        dict: Processing result
    """
    print("[FARGATE] Artifact Processing Service Starting...")
    event_str = json.dumps(event) if isinstance(event, dict) else event
    print(f"[FARGATE] Event: {event_str}")

    # Extract encrypted artifact_id from event
    if isinstance(event, dict):
        encrypted_artifact_id = (
            event.get('encrypted_artifact_id') or
            event.get('artifact_id') or
            event.get('id')
        )
    elif isinstance(event, str):
        encrypted_artifact_id = event
    else:
        encrypted_artifact_id = None

    if not encrypted_artifact_id:
        error_msg = "No artifact_id provided in event"
        print(f"[FARGATE] Error: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }

    # Process the artifact (decryption happens inside)
    result = process_artifact(encrypted_artifact_id)

    print(f"[FARGATE] Processing complete: {json.dumps(result)}")
    return result


def main():
    """
    Main entry point for Fargate container
    Reads encrypted artifact_id from command line arguments
    """
    if len(sys.argv) < 2:
        print("[FARGATE] Error: No encrypted artifact_id provided")
        print("[FARGATE] Usage: python main.py <encrypted_artifact_id>")
        sys.exit(1)

    encrypted_artifact_id = sys.argv[1]
    result = handler(encrypted_artifact_id)

    # Exit with appropriate code
    sys.exit(0 if result.get('success') else 1)


if __name__ == "__main__":
    main()
