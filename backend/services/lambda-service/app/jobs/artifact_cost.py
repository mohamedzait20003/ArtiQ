"""
Artifact Cost Calculator
Returns the download cost (size) of artifacts
"""
import logging
from app.models import Artifact_Model

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda handler for GET /artifact/{artifact_type}/{id}/cost
    Returns the cost (file size in MB) of an artifact
    Args:
        event: {
            'artifact_type': str - Type of artifact (model, dataset, code)
            'artifact_id': str - The artifact ID
            'dependency': bool - Include dependency costs (optional)
        }
        context: Lambda context object
    Returns:
        tuple: (response_data, status_code)
    """
    try:
        logger.info("[COST] Starting artifact cost calculation")

        # Extract parameters
        artifact_type = event.get('artifact_type')
        artifact_id = event.get('artifact_id')
        include_dependencies = event.get('dependency', False)

        logger.info(
            f"[COST] Request - ID: {artifact_id}, "
            f"Type: {artifact_type}, Dependencies: {include_dependencies}"
        )

        # Validate inputs
        if not artifact_id:
            logger.warning("[COST] Missing artifact_id")
            return (
                {'errorMessage': 'artifact_id is required'},
                400
            )

        if not artifact_type:
            logger.warning("[COST] Missing artifact_type")
            return (
                {'errorMessage': 'artifact_type is required'},
                400
            )

        # Retrieve artifact from database
        logger.info(f"[COST] Retrieving artifact: {artifact_id}")
        artifact = Artifact_Model.get({'id': artifact_id})

        if not artifact:
            logger.warning(f"[COST] Artifact not found: {artifact_id}")
            return (
                {'errorMessage': f'Artifact with ID {artifact_id} not found'},
                404
            )

        # Verify artifact type matches
        if artifact.artifact_type != artifact_type:
            logger.warning(
                f"[COST] Type mismatch: expected {artifact_type}, "
                f"got {artifact.artifact_type}"
            )
            return (
                {
                    'errorMessage': (
                        f"Artifact type mismatch: expected {artifact_type}, "
                        f"found {artifact.artifact_type}"
                    )
                },
                400
            )

        # Get file size (in bytes)
        file_size_bytes = artifact.file_size or 0

        # Convert to MB
        file_size_mb = file_size_bytes / (1024 * 1024)

        logger.info(
            f"[COST] Artifact {artifact_id} size: "
            f"{file_size_mb:.2f} MB ({file_size_bytes} bytes)"
        )

        # Build response
        if include_dependencies:
            response = {
                artifact_id: {
                    "standalone_cost": round(file_size_mb, 2),
                    "total_cost": round(file_size_mb, 2)
                }
            }
            logger.info(
                "[COST] Dependencies requested but not yet implemented. "
                "Returning standalone cost only."
            )
        else:
            # Simple response: just total cost
            response = {
                artifact_id: {
                    "total_cost": round(file_size_mb, 2)
                }
            }

        logger.info(f"[COST] Response: {response}")
        return (response, 200)

    except Exception as e:
        logger.error(
            f"[COST] Error calculating artifact cost: {str(e)}",
            exc_info=True
        )
        return (
            {
                'errorMessage': (
                    f'The artifact cost calculator encountered an error: '
                    f'{str(e)}'
                )
            },
            500
        )
