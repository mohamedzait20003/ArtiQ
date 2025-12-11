import os
from .Model import Model
from include import has_one
from typing import Optional, Dict, Any


class Artifact_Model(Model):
    """
    Artifact Model for storing ML models, datasets, and code artifacts.

    Database Schema:
        Table Name: Artifacts
        Primary Key:
            - id (str): Unique identifier for the artifact.
        Attributes:
            - id (str): Unique identifier (Primary Key)
            - name (str): Name of the artifact.
            - artifact_type (str): Type (model, dataset, code).
            - source_url (str): URL or location of the artifact.
            - file_size (Optional[int]): Size in bytes.
            - license (Optional[str]): License information.
            - rating (Optional[Dict[str, Any]]): Ratings/reviews.
            - artifact_content (S3): Content stored in S3.

    s3_fields:
        - artifact_content: Content stored in S3 bucket.
    """

    table_name: str = "Artifacts"
    s3_bucket: Optional[str] = os.environ.get(
        'ARTIFACTS_BUCKET', 'artifacts-bucket'
    )
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
        """Define the primary key for database operations"""
        return ["id"]

    @classmethod
    def scan_artifacts(
        cls,
        name_filter=None,
        types_filter=None,
        limit=None,
        exclusive_start_key=None
    ):
        """
        Scan artifacts table with optional filters

        Args:
            name_filter: Filter by name
            types_filter: List of artifact types to include
            limit: Maximum number of items to return
            exclusive_start_key: Reserved for future pagination support

        Returns:
            {
                'items': [list of artifact instances],
                'last_evaluated_key': None
            }
        """
        try:
            # MongoDB query
            collection = cls.collection()
            query = {}

            # Add name filter
            if name_filter and name_filter != "*":
                query['name'] = name_filter

            # Add type filter
            if types_filter and len(types_filter) > 0:
                valid_types = {'model', 'dataset', 'code'}
                filtered_types = [
                    t for t in types_filter if t in valid_types
                ]
                if filtered_types:
                    query['artifact_type'] = {'$in': filtered_types}

            # Apply limit
            query_limit = limit if limit else 100

            # Execute query
            cursor = collection.find(query).limit(query_limit)
            items = []
            for doc in cursor:
                # Remove MongoDB _id
                if '_id' in doc:
                    del doc['_id']
                items.append(cls(**doc))

            return {
                'items': items,
                'last_evaluated_key': None
            }

        except Exception as e:
            print(f"Error scanning artifacts: {e}")
            return {
                'items': [],
                'last_evaluated_key': None
            }

    def rating(self):
        """
        Get the rating for this artifact (one-to-one relationship)

        Returns:
            Rating_Model instance or None
        """
        from .Rating_Model import Rating_Model
        return has_one(Rating_Model, 'artifact_id', 'id')(self)

    # TODO: Add methods based on OpenAPI spec requirements
