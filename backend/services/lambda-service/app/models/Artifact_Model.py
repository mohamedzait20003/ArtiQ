import os
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
            - artifact_type (str): Type of artifact (e.g., model, dataset, code).
            - source_url (str): URL or location where the artifact can be accessed.
            - file_size (Optional[int]): Size of the artifact file in bytes.
            - license (Optional[str]): License information for the artifact.
            - rating (Optional[Dict[str, Any]]): Ratings or reviews for the artifact.
            - artifact_content (S3): Content of the artifact, stored in S3 (see s3_fields).

    s3_fields:
        - artifact_content: The actual content of the artifact is stored in the S3 bucket defined by s3_bucket.
    """

    table_name: str = "Artifacts"
    s3_bucket: Optional[str] = os.environ.get('ARTIFACTS_BUCKET', 'artifacts-bucket')
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

    @classmethod
    def scan_artifacts(cls, 
                      name_filter=None, 
                      types_filter=None, 
                      limit=None, 
                      exclusive_start_key=None):
        """
        Scan artifacts table with optional filters
        
        Args:
            name_filter: Filter by name (ignored for now)
            types_filter: List of artifact types to include (ignored for now)
            limit: Maximum number of items to return (ignored for now)
            exclusive_start_key: For pagination (ignored for now)
            
        Returns:
            {
                'items': [list of artifact instances],
                'last_evaluated_key': None (no pagination for now)
            }
        """
        try:
            # Build scan parameters
            scan_params = {}
            filter_expressions = []
            
            # Add pagination parameters
            if limit:
                scan_params['Limit'] = limit
            else:
                scan_params['Limit'] = 100  # Default limit of 100
            
            # Add pagination offset (exclusive start key)
            if exclusive_start_key:
                scan_params['ExclusiveStartKey'] = exclusive_start_key
            
            # Add name filter if provided
            if name_filter and name_filter != "*":
                from boto3.dynamodb.conditions import Attr
                filter_expressions.append(Attr('name').eq(name_filter))
            
            # Add type filter if provided
            if types_filter and len(types_filter) > 0:
                # Validate types are valid
                valid_types = {'model', 'dataset', 'code'}
                filtered_types = [t for t in types_filter if t in valid_types]
                
                if filtered_types:
                    from boto3.dynamodb.conditions import Attr
                    filter_expressions.append(Attr('artifact_type').is_in(filtered_types))
            
            # Combine filter expressions with AND
            if filter_expressions:
                combined_filter = filter_expressions[0]
                for expr in filter_expressions[1:]:
                    combined_filter = combined_filter & expr
                scan_params['FilterExpression'] = combined_filter
            
            # Perform the scan with optional filter and pagination
            response = cls.table().scan(**scan_params)
            
            # Convert DynamoDB items to Artifact_Model instances
            items = []
            for item in response.get('Items', []):
                artifact = cls(**item)
                items.append(artifact)
            
            # Get the LastEvaluatedKey for pagination
            last_evaluated_key = response.get('LastEvaluatedKey')
            
            return {
                'items': items,
                'last_evaluated_key': last_evaluated_key
            }
            
        except Exception as e:
            print(f"Error scanning artifacts: {e}")
            return {
                'items': [],
                'last_evaluated_key': None
            }

    # TODO: Add methods based on OpenAPI spec requirements