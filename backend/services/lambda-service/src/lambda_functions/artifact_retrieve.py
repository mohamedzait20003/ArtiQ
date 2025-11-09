import json
from src.models.Artifact_Model import Artifact_Model


def lambda_handler(event, context):
    """
    AWS Lambda handler for GET /artifacts/{artifact_type}/{id}
    Retrieves a specific artifact by type and ID
    """
    try:
        # Extract parameters from event
        artifact_type = event.get('artifact_type')
        artifact_id = event.get('id')
        
        if not artifact_id:
            raise ValueError("Artifact ID is required")
        
        # Retrieve artifact from database
        artifact = Artifact_Model.get({'id': artifact_id}, load_s3_data=False)
        
        if not artifact:
            raise ValueError(f"Artifact with ID {artifact_id} not found")
        
        # Verify artifact type matches (if provided)
        if artifact_type and artifact.artifact_type != artifact_type:
            raise ValueError(f"Artifact type mismatch: expected {artifact_type}, got {artifact.artifact_type}")
        
        # Build response
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
        
        return response_data
        
    except ValueError as e:
        raise Exception(f"Validation error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error retrieving artifact: {str(e)}")

