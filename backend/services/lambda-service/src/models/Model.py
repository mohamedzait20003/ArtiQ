import uuid
from typing import Optional
from abc import ABC, abstractmethod
from botocore.exceptions import ClientError
from src.aws import s3_client, dynamodb


class Model(ABC):
    table_name: str
    s3_bucket: Optional[str] = None
    s3_fields: list[str] = []
    ttl_attribute: Optional[str] = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def table(cls):
        return dynamodb.Table(cls.table_name)

    def _upload_to_s3(self, field_name: str,
                      file_data: bytes) -> Optional[str]:
        """Upload binary data to S3 and return the S3 key"""
        if not self.s3_bucket:
            raise ValueError("s3_bucket must be defined to use S3 storage")

        s3_key = f"{self.table_name}/{field_name}/{uuid.uuid4()}"

        try:
            s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=file_data
            )
            return s3_key
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            return None

    def _download_from_s3(self, s3_key: str) -> Optional[bytes]:
        """Download binary data from S3"""
        if not self.s3_bucket:
            raise ValueError("s3_bucket must be defined to use S3 storage")

        try:
            response = s3_client.get_object(
                Bucket=self.s3_bucket,
                Key=s3_key
            )
            return response['Body'].read()
        except ClientError as e:
            print(f"Error downloading from S3: {e}")
            return None

    def _delete_from_s3(self, s3_key: str) -> bool:
        """Delete file from S3"""
        if not self.s3_bucket:
            return True

        try:
            s3_client.delete_object(
                Bucket=self.s3_bucket,
                Key=s3_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
            return False

    def save(self):
        """Save model to DynamoDB, uploading binary fields to S3"""
        item = self.__dict__.copy()

        for field_name in self.s3_fields:
            if field_name in item and item[field_name] is not None:
                file_data = item[field_name]

                if isinstance(file_data, bytes):
                    s3_key = self._upload_to_s3(field_name, file_data)
                    if s3_key:
                        item[f"{field_name}_s3_key"] = s3_key
                        del item[field_name]
                    else:
                        return False

                elif isinstance(file_data, str):
                    item[f"{field_name}_s3_key"] = file_data
                    del item[field_name]

        try:
            self.table().put_item(Item=item)
            return True
        except ClientError as e:
            print(f"Error saving item: {e}")
            return False

    @classmethod
    def get(cls, key: dict, load_s3_data: bool = False):
        """
        Get item from DynamoDB
        Args:
            key: Primary key to retrieve the item
            load_s3_data: If True, download S3 files into memory
        """
        try:
            response = cls.table().get_item(Key=key)
            item = response.get("Item")
            if item:
                instance = cls(**item)

                if load_s3_data:
                    for field_name in cls.s3_fields:
                        s3_key_field = f"{field_name}_s3_key"
                        if hasattr(instance, s3_key_field):
                            s3_key = getattr(instance, s3_key_field)
                            file_data = instance._download_from_s3(s3_key)
                            if file_data:
                                setattr(instance, field_name, file_data)

                return instance
            return None
        except ClientError as e:
            print(f"Error getting item: {e}")
            return None

    def get_file(self, field_name: str) -> Optional[bytes]:
        """
        Download a specific file from S3
        Args:
            field_name: Name of the field containing the file
        Returns:
            Binary content of the file or None
        """
        if field_name not in self.s3_fields:
            raise ValueError(f"{field_name} is not configured as an S3 field")

        s3_key_field = f"{field_name}_s3_key"
        if hasattr(self, s3_key_field):
            s3_key = getattr(self, s3_key_field)
            return self._download_from_s3(s3_key)
        return None

    def get_file_url(self, field_name: str,
                     expires_in: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for downloading a file from S3

        Args:
            field_name: Name of the field containing the file
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            Presigned URL or None
        """
        if field_name not in self.s3_fields:
            raise ValueError(f"{field_name} is not configured as an S3 field")

        s3_key_field = f"{field_name}_s3_key"
        if not hasattr(self, s3_key_field):
            return None

        s3_key = getattr(self, s3_key_field)

        try:
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.s3_bucket,
                    'Key': s3_key
                },
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None

    def delete(self):
        """Delete item from DynamoDB and associated S3 files"""
        for field_name in self.s3_fields:
            s3_key_field = f"{field_name}_s3_key"
            if hasattr(self, s3_key_field):
                s3_key = getattr(self, s3_key_field)
                self._delete_from_s3(s3_key)

        key = {k: getattr(self, k) for k in self.primary_key()}
        try:
            self.table().delete_item(Key=key)
            return True
        except ClientError as e:
            print(f"Error deleting item: {e}")
            return False

    @classmethod
    @abstractmethod
    def primary_key(cls):
        """
        Define the primary key attributes for DynamoDB operations

        This method must be implemented by all subclasses

        Returns:
            List of attribute names that form the primary key
        """
        pass
