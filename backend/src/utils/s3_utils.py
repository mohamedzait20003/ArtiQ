"""
S3 utility functions for model registry operations.

This module provides helper functions for uploading, downloading, and managing
model files in S3 buckets.
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any, BinaryIO
import json


class S3Manager:
    """Manager class for S3 operations."""
    
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        """
        Initialize S3 manager.
        
        Args:
            bucket_name: Name of the S3 bucket
            region: AWS region
        """
        self.bucket_name = bucket_name
        self.region = region
        self.s3_client = boto3.client("s3", region_name=region)
    
    def upload_file(
        self,
        local_path: str,
        s3_key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Upload a file to S3.
        
        Args:
            local_path: Path to local file
            s3_key: S3 object key
            metadata: Optional metadata to attach to object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = metadata
            
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            return True
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return False
    
    def upload_fileobj(
        self,
        file_obj: BinaryIO,
        s3_key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Upload a file object to S3.
        
        Args:
            file_obj: File-like object
            s3_key: S3 object key
            metadata: Optional metadata to attach to object
            
        Returns:
            True if successful, False otherwise
        """
        try:
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = metadata
            
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            return True
        except ClientError as e:
            print(f"Error uploading file object to S3: {e}")
            return False
    
    def download_file(self, s3_key: str, local_path: str) -> bool:
        """
        Download a file from S3.
        
        Args:
            s3_key: S3 object key
            local_path: Path to save file locally
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.download_file(
                self.bucket_name,
                s3_key,
                local_path
            )
            return True
        except ClientError as e:
            print(f"Error downloading file from S3: {e}")
            return False
    
    def get_object_metadata(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for an S3 object.
        
        Args:
            s3_key: S3 object key
            
        Returns:
            Dictionary of object metadata or None
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return response.get("Metadata", {})
        except ClientError as e:
            print(f"Error getting object metadata: {e}")
            return None
    
    def generate_presigned_upload_url(
        self,
        s3_key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate a presigned URL for uploading.
        
        Args:
            s3_key: S3 object key
            expiration: Expiration time in seconds
            
        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "put_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned upload URL: {e}")
            return ""
    
    def generate_presigned_download_url(
        self,
        s3_key: str,
        expiration: int = 3600
    ) -> str:
        """
        Generate a presigned URL for downloading.
        
        Args:
            s3_key: S3 object key
            expiration: Expiration time in seconds
            
        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned download URL: {e}")
            return ""
    
    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> list:
        """
        List objects in the bucket.
        
        Args:
            prefix: Prefix to filter objects
            max_keys: Maximum number of keys to return
            
        Returns:
            List of object summaries
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            return response.get("Contents", [])
        except ClientError as e:
            print(f"Error listing objects: {e}")
            return []
    
    def delete_object(self, s3_key: str) -> bool:
        """
        Delete an object from S3.
        
        Args:
            s3_key: S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting object: {e}")
            return False


# Factory function for easy access
def get_s3_manager(bucket_name: str) -> S3Manager:
    """
    Get an S3 manager instance.
    
    Args:
        bucket_name: Name of the bucket
        
    Returns:
        S3Manager instance
    """
    return S3Manager(bucket_name)
