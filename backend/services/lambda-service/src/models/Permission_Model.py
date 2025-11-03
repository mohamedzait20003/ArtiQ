from .Model import Model
from typing import Optional, List


class Permission_Model(Model):
    """
    Permission Model for defining system permissions

    DynamoDB Schema:
    - PermissionID (Primary Key): Unique identifier for the permission
    - Title: Permission title (e.g., "Create Models", "Delete Users")
    """

    table_name: str = "Permissions"
    s3_bucket: Optional[str] = None
    s3_fields: list[str] = []

    def __init__(
        self,
        PermissionID: str,
        Title: str,
        **kwargs
    ):
        """
        Initialize Permission_Model instance

        Args:
            PermissionID: Unique identifier (primary key)
            Title: Permission title
        """
        self.PermissionID = PermissionID
        self.Title = Title

        super().__init__(**kwargs)

    @classmethod
    def primary_key(cls):
        """Define the primary key for DynamoDB operations"""
        return ["PermissionID"]

    @classmethod
    def get_by_title(cls, title: str) -> Optional['Permission_Model']:
        """
        Get permission by title

        Args:
            title: The permission title to search for

        Returns:
            Permission_Model instance if found, None otherwise

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
            print(f"Error getting permission by title: {e}")
            return None

    @classmethod
    def list_all(cls) -> List['Permission_Model']:
        """
        List all permissions

        Returns:
            List of Permission_Model instances
        """
        try:
            response = cls.table().scan()
            items = response.get('Items', [])
            return [cls(**item) for item in items]
        except Exception as e:
            print(f"Error listing permissions: {e}")
            return []
