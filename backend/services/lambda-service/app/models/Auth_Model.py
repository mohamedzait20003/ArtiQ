import hashlib
from .Model import Model
from typing import Optional, TYPE_CHECKING
from include import (
    has_one,
    has_one_through,
    active_session_filter
)

if TYPE_CHECKING:
    from .Role_Model import Role_Model
    from .Session_Model import Session_Model


class Auth_Model(Model):
    """
    Authentication Model for user authentication and management

    Database Schema (DocumentDB):
    - ID (Primary Key): Unique identifier for the user
    - Username (Unique, Indexed): User's unique username for login
    - Name: User's display name
    - Email (Unique, Indexed): User's email address
    - Password: Hashed password for authentication
    - RoleID: Foreign key to Role (one-to-one relationship)

    Relationships:
    - role(): Has one Role_Model
    - session(): Has one Session_Model
    """

    table_name: str = "Users"
    s3_bucket: Optional[str] = None
    s3_fields: list[str] = []

    def __init__(
        self,
        ID: str,
        Name: str,
        Email: str,
        Password: str,
        Username: str = "",
        RoleID: str = "",
        **kwargs
    ):
        """
        Initialize Auth_Model instance

        Args:
            ID: Unique identifier (primary key)
            Name: User's display name
            Email: User's email (should be unique and indexed)
            Password: User's hashed password
            Username: User's unique username for login
            RoleID: Role ID assigned to this user
        """
        self.ID = ID
        self.Name = Name
        self.Email = Email
        self.Password = Password
        self.Username = Username if Username else Name
        self.RoleID = RoleID

        super().__init__(**kwargs)

    @classmethod
    def primary_key(cls):
        """Define the primary key for database operations"""
        return ["ID"]

    def save(self):
        """Save user to database, hashing the password before storage"""
        if self.Password and not self._is_hashed(self.Password):
            self.Password = self._hash_password(self.Password)

        return super().save()

    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def _is_hashed(password: str) -> bool:
        """Check if password is already hashed (64 char hex string)"""
        is_correct_length = len(password) == 64
        is_hex = all(c in '0123456789abcdef' for c in password.lower())
        return is_correct_length and is_hex

    def assign_role(self, role_id: str) -> bool:
        """
        Assign a role to this user

        Args:
            role_id: The role ID to assign

        Returns:
            True if successful, False otherwise
        """
        self.RoleID = role_id
        return self.save()

    @property
    def is_admin(self) -> bool:
        """
        Check if user has admin privileges

        Returns:
            True if user has a role with admin privileges, False otherwise
        """
        role = self.role()
        return role and role.Name == 'Admin'

    def role(self) -> Optional['Role_Model']:
        """
        Eloquent-style relationship: Get the role for this user
        One-to-one relationship using HasOneThrough

        Returns:
            Role_Model instance or None
        """
        from .Role_Model import Role_Model
        return has_one_through(
            Role_Model,
            through_key='RoleID',
            foreign_key='RoleID'
        )(self)

    def session(self) -> Optional['Session_Model']:
        """
        Eloquent-style relationship: Get the active session for this user
        One-to-one relationship using HasOne with active filter

        Returns:
            Session_Model instance or None
        """
        from .Session_Model import Session_Model
        return has_one(
            Session_Model,
            foreign_key='UserID',
            local_key='ID',
            filter_callback=active_session_filter
        )(self)

    def get_role(self) -> Optional['Role_Model']:
        """
        Legacy method: Get the role assigned to this user
        Use role() for Eloquent-style access

        Returns:
            Role_Model instance if user has a role, None otherwise
        """
        return self.role()

    @classmethod
    def check_user(
        cls, username: str, password: str
    ) -> Optional['Auth_Model']:
        """
        Authenticate user by username and password
        Args:
            username: The username (Username or Email) to search for
            password: The plain text password to verify
        Returns:
            Auth_Model instance if credentials are valid, None otherwise
        Note: This searches by Username or Email only
        """
        try:
            # MongoDB query with $or operator
            collection = cls.collection()
            item = collection.find_one({
                '$or': [
                    {'Username': username},
                    {'Email': username}
                ]
            })

            if item:
                if '_id' in item:
                    del item['_id']

                user = cls(**item)
                if user.Password == cls._hash_password(password):
                    return user

            return None
        except Exception as e:
            print(f"Error checking user credentials: {e}")
            return None

    @classmethod
    def get_by_email(cls, email: str) -> Optional['Auth_Model']:
        """
        Get user by email address

        Args:
            email: The email address to search for

        Returns:
            Auth_Model instance if found, None otherwise
        """
        try:
            # MongoDB query
            collection = cls.collection()
            item = collection.find_one({'Email': email})

            if item:
                if '_id' in item:
                    del item['_id']
                return cls(**item)

            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
