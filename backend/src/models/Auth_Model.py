import hashlib
from .Model import Model
from typing import Optional


class Auth_Model(Model):
    """
    Authentication Model for user authentication and management

    DynamoDB Schema:
    - ID (Primary Key): Unique identifier for the user
    - Name: User's display name
    - Email (Unique, Indexed): User's email address
    - Password: Hashed password for authentication
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
        **kwargs
    ):
        """
        Initialize Auth_Model instance

        Args:
            ID: Unique identifier (primary key)
            Name: User's display name
            Email: User's email (should be unique and indexed in DynamoDB)
            Password: User's hashed password
        """
        self.ID = ID
        self.Name = Name
        self.Email = Email
        self.Password = Password

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
