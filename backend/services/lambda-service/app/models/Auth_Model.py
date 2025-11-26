import hashlib
from .Model import Model
from .Role_Model import Role_Model
from typing import Optional


class Auth_Model(Model):
    """
    Authentication Model for user authentication and management

    DynamoDB Schema:
    - ID (Primary Key): Unique identifier for the user
    - Name: User's display name
    - Email (Unique, Indexed): User's email address
    - Password: Hashed password for authentication
    - RoleID: ID of the role assigned to this user (one role per user)
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
        RoleID: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Auth_Model instance

        Args:
            ID: Unique identifier (primary key)
            Name: User's display name
            Email: User's email (should be unique and indexed in DynamoDB)
            Password: User's hashed password
            RoleID: Role ID assigned to this user
        """
        self.ID = ID
        self.Name = Name
        self.Email = Email
        self.Password = Password
        self.RoleID = RoleID

        super().__init__(**kwargs)

    @classmethod
    def primary_key(cls):
        """Define the primary key for DynamoDB operations"""
        return ["ID"]

    def save(self):
        """Save user to DynamoDB, hashing the password before storage"""
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

    def get_role(self) -> Optional[Role_Model]:
        """
        Get the role assigned to this user

        Returns:
            Role_Model instance if user has a role, None otherwise
        """
        if self.RoleID:
            return Role_Model.get({"RoleID": self.RoleID})
        return None

    @classmethod
    def check_user(cls, email: str, password: str) -> Optional['Auth_Model']:
        """
        Authenticate user by email and password
        Args:
            email: The email address to search for
            password: The plain text password to verify
        Returns:
            Auth_Model instance if credentials are valid, None otherwise
        Note: This assumes you have a GSI on the Email attribute in DynamoDB
        """
        try:
            response = cls.table().query(
                IndexName='EmailIndex',
                KeyConditionExpression='Email = :email',
                ExpressionAttributeValues={':email': email}
            )

            items = response.get('Items', [])
            if items:
                user = cls(**items[0])
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
        Note: This assumes you have a GSI on the Email attribute in DynamoDB
        """
        try:
            response = cls.table().query(
                IndexName='EmailIndex',
                KeyConditionExpression='Email = :email',
                ExpressionAttributeValues={':email': email}
            )

            items = response.get('Items', [])
            if items:
                return cls(**items[0])
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
