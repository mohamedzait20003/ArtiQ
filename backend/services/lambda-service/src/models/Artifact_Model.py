from .Model import Model
from typing import Optional, Dict, Any


class Artifact_Model(Model):
    """
    Artifact Model for storing machine learning models, datasets, and code artifacts.

    DynamoDB Schema:
        Table Name: Artifacts
        Primary Key:
            - id (str): Unique identifier for the artifact.
        Attributes:
            - id (str): Unique identifier for the artifact. (Primary Key)
            - name (str): Name of the artifact.
            - type (str): Type of artifact (e.g., model, dataset, code).
            - source_url (str): URL or location where the artifact can be accessed.
            - file_size (Optional[int]): Size of the artifact file in bytes.
            - license (Optional[str]): License information for the artifact.
            - rating (Optional[Dict[str, Any]]): Ratings or reviews for the artifact.
            - artifact_content (S3): Content of the artifact, stored in S3 (see s3_fields).

    s3_fields:
        - artifact_content: The actual content of the artifact is stored in the S3 bucket defined by s3_bucket.
    """

    table_name: str = "Artifacts"
    s3_bucket: Optional[str] = "artifacts-bucket"
    s3_fields: list[str] = ["artifact_content"]

    def __init__(
        self,
        id: str,
        name: str,
        artifact_type: str,  # model, dataset, or code
        source_url: str,
        file_size: Optional[int] = None,
        license: Optional[str] = None,
        rating: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize Artifact instance
        """
        self.id = id
        self.name = name
        self.artifact_type = artifact_type
        self.source_url = source_url
        self.file_size = file_size
        self.license = license
        self.rating = rating or {}
        
        super().__init__(**kwargs)

    @classmethod
    def primary_key(cls):
        """Define the primary key for DynamoDB operations"""
        return ["id"]

    # TODO: Add methods based on OpenAPI spec requirements