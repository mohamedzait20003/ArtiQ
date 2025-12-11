"""
Model Artifact Rate Job
Retrieves ratings for a model artifact
"""
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

        # Check if artifact has embedded rating
        logger.info(
            f"[RATE] Checking for rating data on artifact {artifact_id}"
        )
        if not artifact.rating or not isinstance(artifact.rating, dict):
            logger.warning(
                f"[RATE] No rating data found for artifact {artifact_id}"
            )
            return (
                {
                    'errorMessage':
                        f'No rating found for artifact {artifact_id}. '
                        'The artifact may not have been evaluated yet.'
                },
                404
            )

        # Use the embedded rating from the artifact
        rating = artifact.rating
        logger.info(
            f"[RATE] Rating found - net_score: "
            f"{rating.get('net_score', {}).get('value', 'N/A')}"
        )

        # Format response according to ModelRating schema (flattened format)
        response = {
            "name": rating.get("name", artifact.name),
            "category": rating.get("category", ""),
            "net_score": rating.get("net_score", {}).get("value", 0.0),
            "net_score_latency": (
                rating.get("net_score", {}).get("latency", 0.0)
            ),
            "ramp_up_time": (
                rating.get("ramp_up_time", {}).get("value", 0.0)
            ),
            "ramp_up_time_latency": (
                rating.get("ramp_up_time", {}).get("latency", 0.0)
            ),
            "bus_factor": rating.get("bus_factor", {}).get("value", 0.0),
            "bus_factor_latency": (
                rating.get("bus_factor", {}).get("latency", 0.0)
            ),
            "performance_claims": (
                rating.get("performance_claims", {}).get("value", 0.0)
            ),
            "performance_claims_latency": (
                rating.get("performance_claims", {}).get("latency", 0.0)
            ),
            "license": rating.get("license", {}).get("value", 0.0),
            "license_latency": (
                rating.get("license", {}).get("latency", 0.0)
            ),
            "dataset_and_code_score": (
                rating.get("dataset_and_code_score", {}).get("value", 0.0)
            ),
            "dataset_and_code_score_latency": (
                rating.get("dataset_and_code_score", {}).get("latency", 0.0)
            ),
            "dataset_quality": (
                rating.get("dataset_quality", {}).get("value", 0.0)
            ),
            "dataset_quality_latency": (
                rating.get("dataset_quality", {}).get("latency", 0.0)
            ),
            "code_quality": (
                rating.get("code_quality", {}).get("value", 0.0)
            ),
            "code_quality_latency": (
                rating.get("code_quality", {}).get("latency", 0.0)
            ),
            "reproducibility": (
                rating.get("reproducibility", {}).get("value", 0.0)
            ),
            "reproducibility_latency": (
                rating.get("reproducibility", {}).get("latency", 0.0)
            ),
            "reviewedness": (
                rating.get("reviewedness", {}).get("value", 0.0)
            ),
            "reviewedness_latency": (
                rating.get("reviewedness", {}).get("latency", 0.0)
            ),
            "tree_score": rating.get("tree_score", {}).get("value", 0.0),
            "tree_score_latency": (
                rating.get("tree_score", {}).get("latency", 0.0)
            ),
            "size_score": rating.get("size_score", {}).get("value", {
                "raspberry_pi": 0.0,
                "jetson_nano": 0.0,
                "desktop_pc": 0.0,
                "aws_server": 0.0
            }),
            "size_score_latency": (
                rating.get("size_score", {}).get("latency", 0.0)
            )
        }

        logger.info(f"[RATE] Successfully retrieved rating for {artifact_id}")
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
