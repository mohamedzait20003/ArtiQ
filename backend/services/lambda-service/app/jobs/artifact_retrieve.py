import re
from app.models import Artifact_Model


def lambda_handler(event, context):
    """
    AWS Lambda handler for GET /artifacts/{artifact_type}/{id}
    Retrieves a specific artifact by type and ID (BASELINE)

    Returns:
        Artifact object with metadata and data
    Raises:
        Exception with statusCode 400: Missing/invalid fields
        Exception with statusCode 404: Artifact not found
    """
    try:
        # Extract parameters from event
        artifact_type = event.get('artifact_type')
        artifact_id = event.get('id')

        # Validate artifact_type
        if not artifact_type:
            raise ValueError("Artifact type is required")

        valid_types = {'model', 'dataset', 'code'}
        if artifact_type not in valid_types:
            raise ValueError(
                f"Invalid artifact type: {artifact_type}. "
                f"Must be one of {valid_types}"
            )

        # Validate artifact_id format (pattern: ^[a-zA-Z0-9\-]+$)
        if not artifact_id:
            raise ValueError("Artifact ID is required")

        if not re.match(r'^[a-zA-Z0-9\-]+$', artifact_id):
            raise ValueError(
                f"Invalid artifact ID format: {artifact_id}. "
                f"Must match pattern: ^[a-zA-Z0-9\\-]+$"
            )

        # Retrieve artifact from database
        artifact = Artifact_Model.get({'id': artifact_id}, load_s3_data=False)

        if not artifact:
            # Return 404 response
            return (
                {'errorMessage': f"Artifact with ID {artifact_id} not found"},
                404
            )

        # Verify artifact type matches
        if artifact.artifact_type != artifact_type:
            return (
                {
                    'errorMessage': (
                        f"Artifact type mismatch: expected {artifact_type}, "
                        f"got {artifact.artifact_type}"
                    )
                },
                400
            )

        # Build response matching Artifact schema
        response_data = {
            'metadata': {
                'name': artifact.name,
                'id': artifact.id,
                'type': artifact.artifact_type
            },
            'data': {
                'url': artifact.source_url
            }
        }

        return (response_data, 200)

    except ValueError as e:
        # Return 400 response for validation errors
        return (
            {
                'errorMessage': (
                    f"There is missing field(s) in the artifact_type or "
                    f"artifact_id or it is formed improperly, or is "
                    f"invalid: {str(e)}"
                )
            },
            400
        )
    except Exception as e:
        # Return 500 response for unexpected errors
        return (
            {'errorMessage': f"Error retrieving artifact: {str(e)}"},
            500
        )
