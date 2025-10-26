"""
Model Registry database schema and operations.

This module defines the DynamoDB schema for the Model Registry including:
- Models table for storing model metadata
- Users table for authentication/authorization
- Proper primary keys and indexes
"""
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from typing import Optional, Dict, Any, List
from .Model import Model


class ModelRegistry(Model):
    """
    Model registry entry storing metadata about ML models.
    
    Partition Key: model_id (string)
    Sort Key: version (string)
    """
    table_name = "ModelRegistry"
    
    @classmethod
    def primary_key(cls) -> List[str]:
        """Return the primary key fields."""
        return ["model_id", "version"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "created_at" not in self.__dict__:
            self.created_at = datetime.utcnow().isoformat()
        if "updated_at" not in self.__dict__:
            self.updated_at = datetime.utcnow().isoformat()
    
    def update(self):
        """Update the model registry entry."""
        self.updated_at = datetime.utcnow().isoformat()
        key = {k: getattr(self, k) for k in self.primary_key()}
        try:
            self.table().update_item(
                Key=key,
                UpdateExpression="SET updated_at = :updated_at, #data = :data",
                ExpressionAttributeNames={"#data": "data"},
                ExpressionAttributeValues={
                    ":updated_at": self.updated_at,
                    ":data": self.__dict__
                }
            )
            return True
        except ClientError as e:
            print(f"Error updating item: {e}")
            return False
    
    @classmethod
    def list_models(
        cls, 
        owner: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100
    ) -> List["ModelRegistry"]:
        """
        List models with optional filtering.
        
        Args:
            owner: Filter by owner/model author
            tags: Filter by tags
            limit: Maximum number of results
            
        Returns:
            List of ModelRegistry instances
        """
        try:
            table = cls.table()
            
            # Simple scan with filters
            filter_expression = None
            if owner:
                # Note: For production, use GSI on owner field
                pass
            
            response = table.scan(Limit=limit)
            items = response.get("Items", [])
            
            # Filter in Python (not ideal for large datasets)
            if owner:
                items = [item for item in items if item.get("owner") == owner]
            if tags:
                items = [item for item in items if any(tag in item.get("tags", []) for tag in tags)]
            
            return [cls(**item) for item in items]
        except ClientError as e:
            print(f"Error listing models: {e}")
            return []


class User(Model):
    """
    User entry for authentication and authorization.
    
    Partition Key: username (string)
    """
    table_name = "Users"
    
    @classmethod
    def primary_key(cls) -> List[str]:
        """Return the primary key fields."""
        return ["username"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "created_at" not in self.__dict__:
            self.created_at = datetime.utcnow().isoformat()
        if "role" not in self.__dict__:
            self.role = "user"  # default role


# S3 Configuration
def get_s3_client():
    """Get S3 client instance."""
    return boto3.client("s3")


def create_presigned_url(bucket_name: str, object_key: str, expiration: int = 3600) -> str:
    """
    Generate a presigned URL for uploading to S3.
    
    Args:
        bucket_name: Name of the S3 bucket
        object_key: Key for the object to upload
        expiration: URL expiration time in seconds
        
    Returns:
        Presigned URL string
    """
    try:
        s3_client = get_s3_client()
        response = s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=expiration,
        )
        return response
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return ""


def get_presigned_download_url(bucket_name: str, object_key: str, expiration: int = 3600) -> str:
    """
    Generate a presigned URL for downloading from S3.
    
    Args:
        bucket_name: Name of the S3 bucket
        object_key: Key for the object to download
        expiration: URL expiration time in seconds
        
    Returns:
        Presigned URL string
    """
    try:
        s3_client = get_s3_client()
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_key},
            ExpiresIn=expiration,
        )
        return response
    except ClientError as e:
        print(f"Error generating download URL: {e}")
        return ""
