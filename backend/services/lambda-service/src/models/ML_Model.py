from .Model import Model
from typing import Optional, Dict, Any


class ML_Model(Model):
    """
    ML Model for storing machine learning model information

    DynamoDB Schema:
    - ModelID (Primary Key): Unique identifier for the model
    - Title: Model title/name
    - Evaluation: JSON object containing evaluation metrics
    - Metadata: JSON object containing additional model information
    - ModelArtifact: Binary model file stored in S3

    S3 Storage:
    - ModelArtifact_s3_key: S3 key for the model artifact (code/binary)
    """

    table_name: str = "ML_Models"
    s3_bucket: Optional[str] = "ml-models-bucket"  # Configure your bucket
    s3_fields: list[str] = ["ModelArtifact"]

    def __init__(
        self,
        ModelID: str,
        Title: str,
        Evaluation: Optional[Dict[str, Any]] = None,
        Metadata: Optional[Dict[str, Any]] = None,
        ModelArtifact: Optional[bytes] = None,
        **kwargs
    ):
        """
        Initialize ML_Model instance

        Args:
            ModelID: Unique identifier (primary key)
            Title: Model title/name
            Evaluation: Evaluation metrics (stored as JSON)
            Metadata: Additional model metadata (stored as JSON)
            ModelArtifact: Binary model file (stored in S3)
        """
        self.ModelID = ModelID
        self.Title = Title
        self.Evaluation = Evaluation if Evaluation else {}
        self.Metadata = Metadata if Metadata else {}
        self.ModelArtifact = ModelArtifact

        super().__init__(**kwargs)

    @classmethod
    def primary_key(cls):
        """Define the primary key for DynamoDB operations"""
        return ["ModelID"]

    def save(self):
        """
        Save model to DynamoDB
        ModelArtifact will be uploaded to S3 automatically by base class
        """
        return super().save()

    def update_evaluation(
        self, metrics: Dict[str, Any]
    ) -> bool:
        """
        Update evaluation metrics

        Args:
            metrics: Dictionary of evaluation metrics

        Returns:
            True if successful, False otherwise
        """
        self.Evaluation.update(metrics)
        return self.save()

    def update_metadata(
        self, metadata: Dict[str, Any]
    ) -> bool:
        """
        Update model metadata

        Args:
            metadata: Dictionary of metadata to update

        Returns:
            True if successful, False otherwise
        """
        self.Metadata.update(metadata)
        return self.save()

    def get_evaluation_metric(
        self, metric_name: str
    ) -> Optional[Any]:
        """
        Get a specific evaluation metric

        Args:
            metric_name: Name of the metric to retrieve

        Returns:
            Metric value or None if not found
        """
        return self.Evaluation.get(metric_name)

    def get_metadata_field(
        self, field_name: str
    ) -> Optional[Any]:
        """
        Get a specific metadata field

        Args:
            field_name: Name of the metadata field

        Returns:
            Field value or None if not found
        """
        return self.Metadata.get(field_name)

    @classmethod
    def get_by_title(cls, title: str) -> Optional['ML_Model']:
        """
        Get model by title

        Args:
            title: The model title to search for

        Returns:
            ML_Model instance if found, None otherwise

        Note: Requires GSI on Title attribute
        """
        try:
            response = cls.table().query(
                IndexName='TitleIndex',
                KeyConditionExpression='Title = :title',
                ExpressionAttributeValues={':title': title}
            )

            items = response.get('Items', [])
            if items:
                return cls(**items[0])
            return None
        except Exception as e:
            print(f"Error getting model by title: {e}")
            return None

    @classmethod
    def list_all(cls) -> list['ML_Model']:
        """
        List all ML models

        Returns:
            List of ML_Model instances
        """
        try:
            response = cls.table().scan()
            items = response.get('Items', [])
            return [cls(**item) for item in items]
        except Exception as e:
            print(f"Error listing models: {e}")
            return []

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary representation

        Returns:
            Dictionary with model data (excluding binary artifact)
        """
        return {
            'ModelID': self.ModelID,
            'Title': self.Title,
            'Evaluation': self.Evaluation,
            'Metadata': self.Metadata,
            'ModelArtifact_s3_key': getattr(
                self, 'ModelArtifact_s3_key', None
            )
        }
