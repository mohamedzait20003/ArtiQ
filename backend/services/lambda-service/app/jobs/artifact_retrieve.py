import json
import re
from app.models.Artifact_Model import Artifact_Model


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
            raise ValueError(f"Invalid artifact type: {artifact_type}. Must be one of {valid_types}")
        
        # Validate artifact_id format (pattern: ^[a-zA-Z0-9\-]+$)
        if not artifact_id:
            raise ValueError("Artifact ID is required")
        
        if not re.match(r'^[a-zA-Z0-9\-]+$', artifact_id):
            raise ValueError(f"Invalid artifact ID format: {artifact_id}. Must match pattern: ^[a-zA-Z0-9\\-]+$")
        
        # Retrieve artifact from database
        artifact = Artifact_Model.get({'id': artifact_id}, load_s3_data=False)
        
        if not artifact:
            # Return 404 status code
            error_response = {
                'statusCode': 404,
                'errorMessage': f"Artifact with ID {artifact_id} not found"
            }
            raise Exception(json.dumps(error_response))
        
        # Verify artifact type matches
        if artifact.artifact_type != artifact_type:
            error_response = {
                'statusCode': 400,
                'errorMessage': f"Artifact type mismatch: expected {artifact_type}, got {artifact.artifact_type}"
            }
            raise Exception(json.dumps(error_response))
        
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
        
        return response_data
        
    except ValueError as e:
        # Return 400 status code for validation errors
        error_response = {
            'statusCode': 400,
            'errorMessage': f"There is missing field(s) in the artifact_type or artifact_id or it is formed improperly, or is invalid: {str(e)}"
        }
        raise Exception(json.dumps(error_response))
    except Exception as e:
        # If it's already a JSON error response, re-raise it
        error_str = str(e)
        if error_str.startswith('{') and 'statusCode' in error_str:
            raise
        # Otherwise, wrap it as a 500 error
        error_response = {
            'statusCode': 500,
            'errorMessage': f"Error retrieving artifact: {str(e)}"
        }
        raise Exception(json.dumps(error_response))

