"""
Fargate Service - Artifact Processor
Processes artifacts using evaluation pipelines
Designed to be invoked as an ephemeral task from Lambda
"""
import os
import sys
import json
import logging
from datetime import datetime
from include import AWSServices, Pipeline, ParallelGroup
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

# Configure logging for CloudWatch
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

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
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("FARGATE ARTIFACT PROCESSING STARTED")
    logger.info("=" * 60)
    logger.info(f"Timestamp: {start_time.isoformat()}")
    logger.info(f"Encrypted Artifact ID: {encrypted_artifact_id[:50]}...")
    logger.info(f"AWS Region: {os.environ.get('AWS_REGION')}")

    # Log environment variables (excluding sensitive data)
    try:
        # Decrypt the artifact ID
        logger.info("Step 1: Decrypting artifact ID...")
        artifact_id = decrypt_artifact_id(encrypted_artifact_id)
        logger.info(f"Successfully decrypted artifact ID: {artifact_id}")

        # Retrieve artifact from database
        logger.info("Step 2: Retrieving artifact from database...")
        artifact = get_artifact_from_db(artifact_id)

        if not artifact:
            error_msg = f"Artifact {artifact_id} not found in database"
            logger.error(error_msg)
            return {
                'success': False,
                'artifact_id': artifact_id,
                'error': 'Artifact not found'
            }

        logger.info("Successfully retrieved artifact:")
        logger.info(f"  - Name: {artifact.name}")
        logger.info(f"  - Type: {artifact.artifact_type}")
        logger.info(f"  - Source URL: {artifact.source_url}")

        # Execute the evaluation pipeline
        logger.info("=" * 60)
        logger.info("Step 3: Starting Evaluation Pipeline")
        logger.info("=" * 60)
        pipeline_start = datetime.now()

        try:
            logger.info("Pipeline stages:")
            logger.info("  1. Validate Artifact")
            logger.info("  2. Fetch Metadata")
            logger.info("  3. Parallel Evaluation (8 metrics)")
            logger.info("     - Bus Factor")
            logger.info("     - Performance Claims")
            logger.info("     - Ramp-up Time")
            logger.info("     - Size Score")
            logger.info("     - License")
            logger.info("     - Availability")
            logger.info("     - Code Quality")
            logger.info("     - Dataset Quality")
            logger.info("  4. Aggregate Scores")
            logger.info("  5. Save Ratings")

            result = Pipeline(
                validate_artifact_step,
                fetch_metadata_step,
                ParallelGroup(
                    evaluate_bus_factor,
                    # evaluate_performance,
                    # evaluate_rampup,
                    # evaluate_size,
                    # evaluate_license,
                    # evaluate_availability,
                    # evaluate_code_quality,
                    # evaluate_dataset_quality,
                    max_workers=8
                ),
                aggregate_scores_step,
                save_ratings_step
            ).start(artifact)

            pipeline_end = datetime.now()
            pipeline_duration = (pipeline_end - pipeline_start).total_seconds()

            logger.info("=" * 60)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            logger.info(f"Pipeline Duration: {pipeline_duration:.2f} seconds")
            logger.info(f"Net Score: {result.get('net_score', 0.0):.4f}")
            logger.info("Individual Scores:")
            for metric, score in result.get('scores', {}).items():
                logger.info(f"  - {metric}: {score}")
            
            total_duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Total Processing Time: {total_duration:.2f} seconds")
            logger.info("=" * 60)

            return {
                'success': True,
                'artifact_id': artifact_id,
                'artifact_name': artifact.name,
                'artifact_type': artifact.artifact_type,
                'ratings': result.get('scores', {}),
                'net_score': result.get('net_score', 0.0),
                'processing_time_seconds': total_duration
            }

        except Exception as pipeline_error:
            pipeline_end = datetime.now()
            pipeline_duration = (pipeline_end - pipeline_start).total_seconds()
            logger.error("=" * 60)
            logger.error("PIPELINE EXECUTION FAILED")
            logger.error("=" * 60)
            logger.error(f"Error Type: {type(pipeline_error).__name__}")
            logger.error(f"Error Message: {str(pipeline_error)}")
            logger.error(f"Pipeline Duration: {pipeline_duration:.2f} seconds")
            logger.error("Stack Trace:")
            import traceback
            logger.error(traceback.format_exc())
            logger.error("=" * 60)
            raise

    except Exception as e:
        total_duration = (datetime.now() - start_time).total_seconds()
        logger.error("=" * 60)
        logger.error("ARTIFACT PROCESSING FAILED")
        logger.error("=" * 60)
        logger.error(f"Error Type: {type(e).__name__}")
        logger.error(f"Error Message: {str(e)}")
        logger.error(f"Total Duration: {total_duration:.2f} seconds")
        logger.error("Full Stack Trace:")
        import traceback
        logger.error(traceback.format_exc())
        logger.error("=" * 60)
        
        return {
            'success': False,
            'encrypted_artifact_id': encrypted_artifact_id,
            'error': str(e),
            'error_type': type(e).__name__,
            'processing_time_seconds': total_duration
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
    logger.info("*" * 70)
    logger.info("*** FARGATE SERVICE HANDLER INVOKED ***")
    logger.info("*" * 70)
    
    event_str = json.dumps(event) if isinstance(event, dict) else str(event)
    logger.info(f"Event Type: {type(event).__name__}")
    if len(event_str) > 200:
        logger.info(f"Event Data: {event_str[:200]}...")
    else:
        logger.info(f"Event Data: {event_str}")
    
    if context:
        logger.info("Lambda Context Information:")
        request_id = getattr(context, 'aws_request_id', 'N/A')
        func_name = getattr(context, 'function_name', 'N/A')
        remaining_time = getattr(
            context, 'get_remaining_time_in_millis', lambda: 'N/A'
        )()
        logger.info(f"  - Request ID: {request_id}")
        logger.info(f"  - Function Name: {func_name}")
        logger.info(f"  - Remaining Time: {remaining_time}")

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
        logger.error(f"ERROR: {error_msg}")
        logger.error(
            "Expected event format: {'encrypted_artifact_id': 'xxx'} "
            "or string"
        )
        return {
            'success': False,
            'error': error_msg
        }

    artifact_id_len = len(encrypted_artifact_id)
    logger.info(f"Extracted encrypted_artifact_id (length: {artifact_id_len})")

    # Process the artifact (decryption happens inside)
    result = process_artifact(encrypted_artifact_id)

    logger.info("*" * 70)
    success_status = result.get('success', False)
    logger.info(f"*** HANDLER COMPLETE - SUCCESS: {success_status} ***")
    logger.info("*" * 70)
    result_summary = {
        k: v for k, v in result.items()
        if k not in ['ratings', 'error_type']
    }
    logger.info(f"Result Summary: {json.dumps(result_summary, indent=2)}")
    
    return result


def main():
    """
    Main entry point for Fargate container
    Reads encrypted artifact_id from command line arguments
    """
    logger.info("=" * 70)
    logger.info("FARGATE CONTAINER MAIN ENTRY POINT")
    logger.info("=" * 70)
    logger.info(f"Command line arguments: {sys.argv}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")

    if len(sys.argv) < 2:
        logger.error("ERROR: No encrypted artifact_id provided")
        logger.error("Usage: python main.py <encrypted_artifact_id>")
        sys.exit(1)

    encrypted_artifact_id = sys.argv[1]
    artifact_id_len = len(encrypted_artifact_id)
    logger.info(
        f"Processing artifact_id from command line (length: {artifact_id_len})"
    )

    result = handler(encrypted_artifact_id)

    # Exit with appropriate code
    exit_code = 0 if result.get('success') else 1
    logger.info(f"Exiting with code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
