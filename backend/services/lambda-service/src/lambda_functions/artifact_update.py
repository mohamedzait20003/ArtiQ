import json
from src.models.Artifact_Model import Artifact_Model


def lambda_handler(event, context):
    """
    AWS Lambda handler for PUT /artifacts/{artifact_type}/{id}
    Updates an existing artifact
    """
    try:
        # Extract parameters from event
        artifact_type = event.get('artifact_type')
        artifact_id = event.get('id')
        artifact_data = event.get('artifact')
        
        if not artifact_id:
            raise ValueError("Artifact ID is required")
        
        if not artifact_data:
            raise ValueError("Artifact data is required")
        
        # Retrieve existing artifact
        artifact = Artifact_Model.get({'id': artifact_id}, load_s3_data=False)
        
        if not artifact:
            raise ValueError(f"Artifact with ID {artifact_id} not found")
        
        # Verify artifact type matches
        if artifact_type and artifact.artifact_type != artifact_type:
            raise ValueError(f"Artifact type mismatch: expected {artifact_type}, got {artifact.artifact_type}")
        
        # Update artifact fields
        metadata = artifact_data.get('metadata', {})
        data = artifact_data.get('data', {})
        
        # Update name if provided
        if 'name' in metadata:
            artifact.name = metadata['name']
        
        # Update URL if provided
        if 'url' in data:
            artifact.source_url = data['url']
            # If URL changed, we might want to update the file content
            # For now, we'll just update the URL
        
        # Save updated artifact
        save_success = artifact.save()
        
        if not save_success:
            raise Exception("Failed to update artifact in database")
        
        # Return updated artifact
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
        raise Exception(f"Error updating artifact: {str(e)}")

