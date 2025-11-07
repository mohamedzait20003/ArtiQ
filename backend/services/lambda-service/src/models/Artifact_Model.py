from .Model import Model
from typing import Optional, Dict, Any


class Artifact_Model(Model):
    """
    Artifact Model for storing machine learning models, datasets, and code artifacts
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