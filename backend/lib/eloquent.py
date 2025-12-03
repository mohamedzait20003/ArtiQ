import uuid
from typing import Optional
from abc import ABC, abstractmethod
from botocore.exceptions import ClientError
from lib.aws import get_s3, get_collection


class Eloquent(ABC):
    table_name: str
    s3_bucket: Optional[str] = None
    s3_fields: list[str] = []
    ttl_attribute: Optional[str] = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def collection(cls):
        """Get DocumentDB/MongoDB collection"""
        return get_collection(cls.table_name)

    def _upload_to_s3(self, field_name: str,
                      file_data: bytes) -> Optional[str]:
        """Upload binary data to S3 and return the S3 key"""
        if not self.s3_bucket:
            raise ValueError("s3_bucket must be defined to use S3 storage")

        s3_key = f"{self.table_name}/{field_name}/{uuid.uuid4()}"

        try:
            get_s3().put_object(
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
            response = get_s3().get_object(
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
            get_s3().delete_object(
                Bucket=self.s3_bucket,
                Key=s3_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
            return False

    def save(self):
        """Save model to database, uploading binary fields to S3"""
        item = self.__dict__.copy()

        # Handle S3 fields
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
            # MongoDB upsert operation
            collection = self.collection()
            filter_query = {k: item[k] for k in self.primary_key()}
            collection.replace_one(
                filter_query,
                item,
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error saving item: {e}")
            return False

    @classmethod
    def get(cls, key: dict, load_s3_data: bool = False):
        """
        Get item from database

        Args:
            key: Primary key to retrieve the item
            load_s3_data: If True, download S3 files into memory
        """
        try:
            # MongoDB findOne operation
            collection = cls.collection()
            item = collection.find_one(key)

            if item:
                # Remove MongoDB _id if present
                if '_id' in item:
                    del item['_id']

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
        except Exception as e:
            print(f"Error getting item: {e}")
            return None

    @classmethod
    def where(cls, query: dict, load_s3_data: bool = False):
        """
        Get multiple items from database matching query

        Args:
            query: MongoDB query filter
            load_s3_data: If True, download S3 files into memory

        Returns:
            List of model instances
        """
        try:
            collection = cls.collection()
            cursor = collection.find(query)
            results = []

            for item in cursor:
                # Remove MongoDB _id if present
                if '_id' in item:
                    del item['_id']

                instance = cls(**item)

                if load_s3_data:
                    for field_name in cls.s3_fields:
                        s3_key_field = f"{field_name}_s3_key"
                        if hasattr(instance, s3_key_field):
                            s3_key = getattr(instance, s3_key_field)
                            file_data = instance._download_from_s3(s3_key)
                            if file_data:
                                setattr(instance, field_name, file_data)

                results.append(instance)

            return results
        except Exception as e:
            print(f"Error querying items: {e}")
            return []

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
            url = get_s3().generate_presigned_url(
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
        """Delete item from database and associated S3 files"""
        key = {k: getattr(self, k) for k in self.primary_key()}

        # Handle CASCADE deletes for dependent records
        self._cascade_delete()

        # Delete S3 files
        for field_name in self.s3_fields:
            s3_key_field = f"{field_name}_s3_key"
            if hasattr(self, s3_key_field):
                s3_key = getattr(self, s3_key_field)
                self._delete_from_s3(s3_key)

        try:
            # MongoDB deleteOne operation
            collection = self.collection()
            result = collection.delete_one(key)
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting item: {e}")
            return False

    def _cascade_delete(self):
        """Handle CASCADE deletes for dependent records"""
        # Get all relationship methods defined on this model
        for attr_name in dir(self.__class__):
            attr = getattr(self.__class__, attr_name)

            # Check if it's a has_one or has_many relationship
            if callable(attr) and hasattr(attr, '__self__'):
                continue

            # Try to get the relationship descriptor
            try:
                if attr_name.startswith('_'):
                    continue

                relationship = getattr(self, attr_name)

                # Check if it's a relationship that should cascade
                if callable(relationship):
                    result = relationship()

                    # Delete related records
                    if result is not None:
                        if isinstance(result, list):
                            for related in result:
                                if hasattr(related, 'delete'):
                                    related.delete()
                        elif hasattr(result, 'delete'):
                            result.delete()
            except Exception:
                # Skip attributes that aren't relationships
                continue

    @classmethod
    @abstractmethod
    def primary_key(cls):
        """
        Define the primary key attributes for database operations

        This method must be implemented by all subclasses

        Returns:
            List of attribute names that form the primary key
        """
        pass
