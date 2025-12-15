"""
Job: Get First 10 Artifacts by Type
Retrieves the first 10 artifacts of a specified type
"""

from app.models.Artifact_Model import Artifact_Model


def lambda_handler(event, context):
    """
    Get the first 10 artifacts of a specific type

    Args:
        event: Dict with 'artifact_type' key

    Returns:
        Tuple of (response_dict, status_code)
    """
    try:
        # Extract artifact_type from event
        artifact_type = event.get('artifact_type')

        # Validate artifact_type
        if not artifact_type:
            return {
                'errorMessage': 'Missing artifact_type parameter'
            }, 400

        valid_types = {'model', 'dataset', 'code'}
        if artifact_type not in valid_types:
            return {
                'errorMessage': (
                    f'Invalid artifact_type. Must be one of: '
                    f'{", ".join(valid_types)}'
                )
            }, 400

        print(f"Fetching first 10 artifacts of type: {artifact_type}")

        # Scan artifacts filtered by type, limit to 10
        result_dict = Artifact_Model.scan_artifacts(
            types_filter=[artifact_type],
            limit=10
        )

        # Extract the items list from the result
        artifacts = result_dict.get('items', [])

        # If no artifacts found
        if not artifacts:
            return {
                'errorMessage': (
                    f'No artifacts found for type: {artifact_type}'
                )
            }, 404

        print(f"Found {len(artifacts)} artifacts of type {artifact_type}")

        # Format response - return list of artifact objects
        result = []
        for artifact in artifacts:
            artifact_dict = {
                'id': artifact.id,
                'name': artifact.name,
                'size': artifact.size if hasattr(artifact, 'size') else None,
                'description': artifact.description if hasattr(artifact, 'description') else None
            }
            result.append(artifact_dict)

        return result, 200

    except Exception as e:
        print(f"Error in artifact_first_ten_by_type: {str(e)}")
        return {
            'errorMessage': (
                f'Error retrieving first 10 artifacts by type: {str(e)}'
            )
        }, 500
