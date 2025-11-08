import json
import uuid


def lambda_handler(event, context):
    """
    AWS Lambda handler for POST /artifact/{artifact_type}
    Creates a new artifact
    """
    try:
        # Extract parameters from event
        artifact_type = event.get('artifact_type')
        artifact_data = event.get('artifact_data')
        
        # TODO: Implement interaction with Artifact_Model and storage logic
        
        # Generate a mock artifact ID
        artifact_id = str(uuid.uuid4())[:10]
        
        # Extract name from URL (simple extraction for demo)
        url = artifact_data.get('url', '')
        name = url.split('/')[-1] if url else 'unknown-artifact'
        
        response_data = {
            'metadata': {
                'name': name,
                'id': artifact_id,
                'type': artifact_type
            },
            'data': {
                'url': artifact_data.get('url')
            }
        }
        
        return response_data
        
    except Exception as e:
        raise Exception(f"Error creating artifact: {str(e)}")