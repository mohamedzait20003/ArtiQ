from .Model import Model
from typing import Optional, List


class Role_Model(Model):
    """
    Role Model for defining user roles with permissions

    DynamoDB Schema:
    - RoleID (Primary Key): Unique identifier for the role
    - Name: Role name (e.g., "Admin", "User", "Viewer")
    - Description: Human-readable description of the role
    - PermissionIDs: List of permission IDs assigned to this role
    """

    table_name: str = "Roles"
    s3_bucket: Optional[str] = None
    s3_fields: list[str] = []

    def __init__(
        self,
        RoleID: str,
        Name: str,
        Description: str,
        PermissionIDs: List[str] = None,
        **kwargs
    ):
        """
        Initialize Role_Model instance

        Args:
            RoleID: Unique identifier (primary key)
            Name: Role name
            Description: What this role is for
            PermissionIDs: List of permission IDs assigned to this role
        """
        self.RoleID = RoleID
        self.Name = Name
        self.Description = Description
        self.PermissionIDs = PermissionIDs if PermissionIDs else []

        super().__init__(**kwargs)

    @classmethod
    def primary_key(cls):
        """Define the primary key for DynamoDB operations"""
        return ["RoleID"]

    def add_permission(self, permission_id: str) -> bool:
        """
        Add a permission to this role

        Args:
            permission_id: The permission ID to add

        Returns:
            True if successful, False otherwise
        """
        if permission_id not in self.PermissionIDs:
            self.PermissionIDs.append(permission_id)
            return self.save()
        return True

    def remove_permission(self, permission_id: str) -> bool:
        """
        Remove a permission from this role

        Args:
            permission_id: The permission ID to remove

        Returns:
            True if successful, False otherwise
        """
        if permission_id in self.PermissionIDs:
            self.PermissionIDs.remove(permission_id)
            return self.save()
        return True

    @classmethod
    def get_by_name(cls, name: str) -> Optional['Role_Model']:
        """
        Get role by name

        Args:
            name: The role name to search for

        Returns:
            Role_Model instance if found, None otherwise

        Note: Requires GSI on Name attribute
        """
        try:
            response = cls.table().query(
                IndexName='NameIndex',
                KeyConditionExpression='Name = :name',
                ExpressionAttributeValues={':name': name}
            )

            items = response.get('Items', [])
            if items:
                return cls(**items[0])
            return None
        except Exception as e:
            print(f"Error getting role by name: {e}")
            return None

    @classmethod
    def list_all(cls) -> List['Role_Model']:
        """
        List all roles

        Returns:
            List of Role_Model instances
        """
        try:
            response = cls.table().scan()
            items = response.get('Items', [])
            return [cls(**item) for item in items]
        except Exception as e:
            print(f"Error listing roles: {e}")
            return []
