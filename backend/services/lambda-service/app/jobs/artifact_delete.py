import re
import json
from app.models.Artifact_Model import Artifact_Model


def lambda_handler(event, context):
    """
    AWS Lambda handler for DELETE /artifacts/{artifact_type}/{id}
    Deletes a specific artifact by type and ID (NON-BASELINE)
    Returns:
        Success message
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
            raise ValueError(f"Invalid artifact type: {artifact_type}. Must be one of {valid_types}")

        # Validate artifact_id format (pattern: ^[a-zA-Z0-9\-]+$)
        if not artifact_id:
            raise ValueError("Artifact ID is required")

        if not re.match(r'^[a-zA-Z0-9\-]+$', artifact_id):
            raise ValueError(f"Invalid artifact ID format: {artifact_id}. Must match pattern: ^[a-zA-Z0-9\\-]+$")

        # Retrieve artifact from database
        artifact = Artifact_Model.get({'id': artifact_id}, load_s3_data=False)

        if not artifact:
            return (
                {'errorMessage': f"Artifact with ID {artifact_id} not found"},
                404
            )

        # Verify artifact type matches
        if artifact.artifact_type != artifact_type:
            return (
                {'errorMessage': f"Artifact type mismatch: expected {artifact_type}, got {artifact.artifact_type}"},
                400
            )

        # Delete artifact (this will also delete S3 files)
        delete_success = artifact.delete()

        if not delete_success:
            return (
                {'errorMessage': "Failed to delete artifact from database and S3"},
                500
            )

        # Return success (spec says 200 with no specific body, but we'll return a message)
        return ({"message": "Artifact is deleted."}, 200)

    except ValueError as e:
        # Return 400 response for validation errors
        return (
            {'errorMessage': f"There is missing field(s) in the artifact_type or artifact_id or invalid: {str(e)}"},
            400
        )
    except Exception as e:
        # Return 500 response for unexpected errors
        return (
            {'errorMessage': f"Error deleting artifact: {str(e)}"},
            500
        )

