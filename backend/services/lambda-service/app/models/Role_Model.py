from .Model import Model
from typing import Optional, List, TYPE_CHECKING
from include import has_many

if TYPE_CHECKING:
    from .Auth_Model import Auth_Model


class Role_Model(Model):
    """
    Role Model for defining user roles with permissions

    Database Schema:
    - RoleID (Primary Key): Unique identifier for the role
    - Name: Role name (e.g., "Admin", "User", "Viewer")
    - Description: Human-readable description of the role
    - PermissionIDs: List of permission IDs assigned to this role

    Relationships:
    - users(): Has many Auth_Model (one-to-many)
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
        """Define the primary key for database operations"""
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
        """
        try:
            # MongoDB query
            collection = cls.collection()
            doc = collection.find_one({'Name': name})
            if doc:
                if '_id' in doc:
                    del doc['_id']
                return cls(**doc)
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
            # MongoDB query
            collection = cls.collection()
            cursor = collection.find({})
            items = []
            for doc in cursor:
                if '_id' in doc:
                    del doc['_id']
                items.append(cls(**doc))
            return items
        except Exception as e:
            print(f"Error listing roles: {e}")
            return []

    def users(self) -> List['Auth_Model']:
        """
        Eloquent-style relationship: Get all users with this role
        One-to-many relationship using HasMany

        Returns:
            List of Auth_Model instances
        """
        from .Auth_Model import Auth_Model
        return has_many(
            Auth_Model,
            foreign_key='RoleID',
            local_key='RoleID'
        )(self)
