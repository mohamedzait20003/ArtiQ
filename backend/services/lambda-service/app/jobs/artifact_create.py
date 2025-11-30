import uuid
from app.models.Artifact_Model import Artifact_Model


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

        # Generate an artifact ID
        artifact_id = str(uuid.uuid4())

        # Extract name from URL (simple extraction for demo)
        url = artifact_data.get('url', '')
        name = url.split('/')[-1] if url else 'unknown-artifact'

        # Create a mock artifact file (empty file as placeholder)
        mock_file_content = f"Mock {artifact_type} file for {name}\nSource: {url}\nGenerated at: {artifact_id}".encode('utf-8')

        # Save to database using Artifact_Model
        artifact = Artifact_Model(
            id=artifact_id,
            name=name,
            artifact_type=artifact_type,
            source_url=url,
            file_size=len(mock_file_content),
            license=None,
            rating=None
        )

        # Store the mock file content in S3
        artifact.artifact_content = mock_file_content
        save_success = artifact.save()

        if not save_success:
            raise Exception("Failed to save artifact to database")

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
