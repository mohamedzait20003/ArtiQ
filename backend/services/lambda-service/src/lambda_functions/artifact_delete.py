import json
from src.models.Artifact_Model import Artifact_Model


def lambda_handler(event, context):
    """
    AWS Lambda handler for DELETE /artifacts/{artifact_type}/{id}
    Deletes an artifact
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
        
        # Delete artifact (this will also delete S3 files)
        delete_success = artifact.delete()
        
        if not delete_success:
            raise Exception("Failed to delete artifact from database")
        
        # Return success message
        return {
            'message': f'Artifact {artifact_id} deleted successfully'
        }
        
    except ValueError as e:
        raise Exception(f"Validation error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error deleting artifact: {str(e)}")

