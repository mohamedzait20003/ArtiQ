"""
Model Artifact Rate Job
Retrieves ratings for a model artifact
"""
import time
import logging
from app.models import Artifact_Model

# Configure logger for CloudWatch
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda handler for GET /artifact/model/{id}/rate
    Retrieves rating information for a model artifact

    Args:
        event: {
            'artifact_id': str - The model artifact ID
        }
        context: Lambda context object

    Returns:
        tuple: (response_data, status_code)
    """
    try:
        logger.info("[RATE] Starting model artifact rate request")

        # Extract artifact_id from event
        artifact_id = event.get('artifact_id')
        logger.info(f"[RATE] Requested artifact ID: {artifact_id}")

        if not artifact_id:
            logger.warning("[RATE] artifact_id is missing from request")
            return (
                {'errorMessage': 'artifact_id is required'},
                400
            )

        # Retrieve the artifact from database
        logger.info(f"[RATE] Retrieving artifact from database: {artifact_id}")
        artifact = Artifact_Model.get({'id': artifact_id})

        if not artifact:
            logger.warning(f"[RATE] Artifact not found: {artifact_id}")
            return (
                {'errorMessage': f'Artifact {artifact_id} does not exist'},
                404
            )

        logger.info(
            f"[RATE] Artifact found: {artifact.name} "
            f"(type: {artifact.artifact_type})"
        )

        # Verify it's a model artifact
        if artifact.artifact_type != 'model':
            logger.warning(
                f"[RATE] Artifact type mismatch: expected 'model', "
                f"got '{artifact.artifact_type}'"
            )
            return (
                {
                    'errorMessage':
                        f'Artifact {artifact_id} is not a model artifact'
                },
                400
            )

        # Get rating via relationship with optimized retry logic
        logger.info(
            f"[RATE] Fetching rating for artifact {artifact_id}"
        )
        rating_obj = artifact.rating()

        # Optimized polling: exponential backoff + early termination
        # Fast checks initially, slower as time progresses
        if not rating_obj:
            logger.info(
                f"[RATE] No rating found for artifact {artifact_id}. "
                "Starting optimized polling..."
            )

            # Aggressive polling for first 10s (most evals complete quickly)
            for attempt in range(1, 11):  # 10 attempts * 1s = 10s
                time.sleep(1)
                rating_obj = artifact.rating()
                if rating_obj:
                    logger.info(
                        f"[RATE] Rating found after {attempt}s "
                        f"(fast polling)"
                    )
                    break

            # Medium polling for next 20s
            if not rating_obj:
                for attempt in range(1, 11):  # 10 attempts * 2s = 20s
                    time.sleep(2)
                    rating_obj = artifact.rating()
                    if rating_obj:
                        logger.info(
                            f"[RATE] Rating found after {10 + attempt * 2}s "
                            f"(medium polling)"
                        )
                        break

            # Slow polling for remaining time (up to 3 minutes total)
            if not rating_obj:
                for attempt in range(1, 27):  # 26 attempts * 5s = 130s
                    time.sleep(5)
                    rating_obj = artifact.rating()
                    if rating_obj:
                        logger.info(
                            f"[RATE] Rating found after "
                            f"{30 + attempt * 5}s (slow polling)"
                        )
                        break

            # Final check - if still not available
            if not rating_obj:
                logger.warning(
                    f"[RATE] No rating found for artifact {artifact_id} "
                    f"after 3 minutes of polling"
                )
                return (
                    {
                        'errorMessage':
                            f'No rating found for artifact {artifact_id}. '
                            'The artifact evaluation is taking longer than '
                            'expected. Please try again in a few minutes.'
                    },
                    404
                )

        logger.info(
            f"[RATE] Rating found - net_score: "
            f"{rating_obj.net_score.get('value', 'N/A')}"
        )

        # Format response according to ModelRating schema (flattened format)
        response = {
            "name": artifact.name,
            "category": getattr(artifact, 'category', 'unknown'),
            "net_score": rating_obj.net_score.get("value", 0.0),
            "net_score_latency": (
                rating_obj.net_score.get("latency", 0.0)
            ),
            "ramp_up_time": (
                rating_obj.ramp_up_time.get("value", 0.0)
            ),
            "ramp_up_time_latency": (
                rating_obj.ramp_up_time.get("latency", 0.0)
            ),
            "bus_factor": rating_obj.bus_factor.get("value", 0.0),
            "bus_factor_latency": (
                rating_obj.bus_factor.get("latency", 0.0)
            ),
            "performance_claims": (
                rating_obj.performance_claims.get("value", 0.0)
            ),
            "performance_claims_latency": (
                rating_obj.performance_claims.get("latency", 0.0)
            ),
            "license": rating_obj.license.get("value", 0.0),
            "license_latency": (
                rating_obj.license.get("latency", 0.0)
            ),
            "dataset_and_code_score": (
                rating_obj.dataset_and_code_score.get("value", 0.0)
            ),
            "dataset_and_code_score_latency": (
                rating_obj.dataset_and_code_score.get("latency", 0.0)
            ),
            "dataset_quality": (
                rating_obj.dataset_quality.get("value", 0.0)
            ),
            "dataset_quality_latency": (
                rating_obj.dataset_quality.get("latency", 0.0)
            ),
            "code_quality": (
                rating_obj.code_quality.get("value", 0.0)
            ),
            "code_quality_latency": (
                rating_obj.code_quality.get("latency", 0.0)
            ),
            "reproducibility": (
                rating_obj.reproducibility.get("value", 0.0)
            ),
            "reproducibility_latency": (
                rating_obj.reproducibility.get("latency", 0.0)
            ),
            "reviewedness": (
                rating_obj.reviewedness.get("value", 0.0)
            ),
            "reviewedness_latency": (
                rating_obj.reviewedness.get("latency", 0.0)
            ),
            "tree_score": rating_obj.tree_score.get("value", 0.0),
            "tree_score_latency": (
                rating_obj.tree_score.get("latency", 0.0)
            ),
            "size_score": rating_obj.size_score.get("value", {
                "raspberry_pi": 0.0,
                "jetson_nano": 0.0,
                "desktop_pc": 0.0,
                "aws_server": 0.0
            }),
            "size_score_latency": (
                rating_obj.size_score.get("latency", 0.0)
            )
        }

        logger.info(f"[RATE] Successfully retrieved rating for {artifact_id}")
        logger.info(f"[RATE] Final response for CloudWatch: {response}")
        return (response, 200)

    except Exception as e:
        logger.error(
            f"[RATE] Error in model_artifact_rate: {str(e)}",
            exc_info=True
        )
        return (
            {
                'errorMessage':
                    f'The artifact rating system encountered an error: '
                    f'{str(e)}'
            },
            500
        )
