import time
import hashlib
from .Model import Model
from typing import Optional


class Session_Model(Model):
    """
    Session Model for managing user sessions with TTL

    DynamoDB Schema:
    - ID (Primary Key): Unique session identifier
    - UserID: Foreign key reference to Users table
    - Token: Hashed session token for authentication
    - TTL: Time-to-live timestamp for automatic session expiration
    """

    table_name: str = "Sessions"
    s3_bucket: Optional[str] = None
    s3_fields: list[str] = []
    ttl_attribute: str = "TTL"

    def __init__(
        self,
        ID: str,
        UserID: str,
        Token: str,
        TTL: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize Session_Model instance

        Args:
            ID: Unique session identifier (primary key)
            UserID: Reference to the user's ID in Users table
            Token: Session token (will be hashed before storage)
            TTL: Unix timestamp for session expiration (auto-calculated)
        """
        self.ID = ID
        self.UserID = UserID
        self.Token = Token
        self.TTL = TTL or self._calculate_ttl()

        super().__init__(**kwargs)

    @classmethod
    def primary_key(cls):
        """Define the primary key for DynamoDB operations"""
        return ["ID"]

    @staticmethod
    def _calculate_ttl(hours: int = 1) -> int:
        """
        Calculate TTL timestamp (default: 1 hour from now)
        Args:
            hours: Number of hours until expiration
        Returns:
            Unix timestamp for expiration
        """
        return int(time.time()) + (hours * 60 * 60)

    def save(self):
        """Save session to DynamoDB, hashing the token before storage"""
        # Hash the token if it's not already hashed
        if self.Token and not self._is_hashed(self.Token):
            self.Token = self._hash_token(self.Token)

        # Ensure TTL is set
        if not self.TTL:
            self.TTL = self._calculate_ttl()

        return super().save()

    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash a token using SHA-256"""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def _is_hashed(token: str) -> bool:
        """Check if token is already hashed (64 char hex string)"""
        is_correct_length = len(token) == 64
        is_hex = all(c in '0123456789abcdef' for c in token.lower())
        return is_correct_length and is_hex

    @classmethod
    def get_by_user_id(cls, user_id: str) -> list['Session_Model']:
        """
        Get all active sessions for a user

        Args:
            user_id: The user ID to search for

        Returns:
            List of Session_Model instances

        Note: Requires a GSI on UserID attribute
        """
        try:
            response = cls.table().query(
                IndexName='UserIDIndex',
                KeyConditionExpression='UserID = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )

            items = response.get('Items', [])
            return [cls(**item) for item in items]
        except Exception as e:
            print(f"Error querying sessions by user ID: {e}")
            return []

    @classmethod
    def verify_session(
        cls, session_id: str, token: str
    ) -> Optional['Session_Model']:
        """
        Verify a session by ID and token

        Args:
            session_id: The session ID
            token: The plain text token to verify

        Returns:
            Session_Model instance if valid, None otherwise
        """
        try:
            session = cls.get({'ID': session_id})
            if session:
                hashed_token = cls._hash_token(token)
                if session.Token == hashed_token:
                    # Check if session hasn't expired
                    if session.TTL > int(time.time()):
                        return session
            return None
        except Exception as e:
            print(f"Error verifying session: {e}")
            return None
