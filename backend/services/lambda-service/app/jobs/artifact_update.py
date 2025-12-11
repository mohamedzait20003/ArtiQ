import re
from app.models import Artifact_Model


def lambda_handler(event, context):
    """
    AWS Lambda handler for PUT /artifacts/{artifact_type}/{id}
    Updates an existing artifact (BASELINE)

    The name and id must match (per spec requirement).

    Returns:
        Updated Artifact object with metadata and data
    Raises:
        Exception with statusCode 400: Missing/invalid fields or
            name/id mismatch
        Exception with statusCode 404: Artifact not found
    """
    try:
        # Extract parameters from event
        artifact_type = event.get('artifact_type')
        artifact_id = event.get('id')
        artifact_data = event.get('artifact')

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

        # Validate artifact_data structure
        if not artifact_data:
            raise ValueError("Artifact data is required")

        metadata = artifact_data.get('metadata')
        data = artifact_data.get('data')

        if not metadata:
            raise ValueError("Artifact metadata is required")

        if not data:
            raise ValueError("Artifact data is required")

        # CRITICAL: The spec says "The name and id must match"
        # This means the metadata.id must match the path id, and
        # metadata.name must match the existing artifact name
        request_id = metadata.get('id')
        request_name = metadata.get('name')

        if not request_id:
            raise ValueError("Artifact metadata.id is required")

        if not request_name:
            raise ValueError("Artifact metadata.name is required")

        # Validate that metadata.id matches path id
        if request_id != artifact_id:
            return (
                {
                    'errorMessage': (
                        f"The name and id must match. Path id: "
                        f"{artifact_id}, metadata id: {request_id}"
                    )
                },
                400
            )

        # Retrieve existing artifact
        artifact = Artifact_Model.get({'id': artifact_id}, load_s3_data=False)

        if not artifact:
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

        # Validate that metadata.name matches existing artifact name
        if request_name != artifact.name:
            return (
                {
                    'errorMessage': (
                        f"The name and id must match. Existing name: "
                        f"{artifact.name}, request name: {request_name}"
                    )
                },
                400
            )

        # Update URL if provided (the spec says "The artifact source
        # (from artifact_data) will replace the previous contents")
        if 'url' in data:
            artifact.source_url = data['url']
            # If URL changed, we might want to update the file content
            # For now, we'll just update the URL

        # Save updated artifact
        save_success = artifact.save()

        if not save_success:
            return (
                {'errorMessage': "Failed to update artifact in database"},
                500
            )

        # Return updated artifact matching Artifact schema
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
            {'errorMessage': f"Error updating artifact: {str(e)}"},
            500
        )
