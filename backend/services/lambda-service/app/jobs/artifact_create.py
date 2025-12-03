import uuid
from app.models import Artifact_Model
from app.utils import send_artifact_to_sqs, url_to_artifact_name


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

        # Extract URL from artifact data
        url = artifact_data.get('url', '')

        # Generate artifact name from URL
        artifact_name = url_to_artifact_name(url)

        # Create artifact instance
        artifact = Artifact_Model(
            id=artifact_id,
            name=artifact_name,
            artifact_type=artifact_type,
            source_url=url,
            file_size=None,
            license=None,
            rating=None
        )

        # Create a mock artifact file (empty file as placeholder)
        mock_file_content = (
            f"Mock {artifact_type} file for {artifact.name}\n"
            f"Source: {url}\nGenerated at: {artifact_id}"
        ).encode('utf-8')

        # Update file size and store content in S3
        artifact.file_size = len(mock_file_content)
        artifact.artifact_content = mock_file_content
        save_success = artifact.save()

        if not save_success:
            raise Exception("Failed to save artifact to database")

        # Send encrypted artifact ID to SQS for processing
        send_artifact_to_sqs(artifact_id, artifact_type)

        response_data = {
            'metadata': {
                'name': artifact.name,
                'id': artifact_id,
                'type': artifact_type
            },
            'data': {
                'url': artifact_data.get('url')
            }
        }

        return (response_data, 201)

    except Exception as e:
        return (
            {'errorMessage': f"Error creating artifact: {str(e)}"},
            500
        )
