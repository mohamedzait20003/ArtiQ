"""
Artifact utility functions for the Fargate service
"""
from app.models.Artifact_Model import Artifact_Model


def get_artifact_from_db(artifact_id: str):
    """
    Retrieve artifact from database by ID

    Args:
        artifact_id: The artifact ID to retrieve

    Returns:
        Artifact object or None if not found
    """
    try:
        artifact = Artifact_Model.get(
            {'id': artifact_id},
            load_s3_data=False
        )
        return artifact
    except Exception as e:
        print(f"[FARGATE] Error retrieving artifact {artifact_id}: {e}")
        return None
