import time
import hashlib
from .Model import Model
from typing import Optional, TYPE_CHECKING
from include import belong_to_one

if TYPE_CHECKING:
    from .Auth_Model import Auth_Model


class Session_Model(Model):
    """
    Session Model for managing user sessions with TTL
    One-to-one relationship: Each user has exactly one active session

    Database Schema:
    - ID (Primary Key): Unique session identifier
    - UserID: Foreign key reference to Users table (unique constraint)
    - Token: Hashed session token for authentication
    - TTL: Time-to-live timestamp for automatic session expiration

    Relationships:
    - user(): Belongs to one Auth_Model
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
        """Define the primary key for database operations"""
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
    def get_by_user_id(cls, user_id: str) -> Optional['Session_Model']:
        """
        Get the active session for a user (one-to-one relationship)

        Args:
            user_id: The user ID to search for

        Returns:
            Session_Model instance or None
        """
        try:
            # MongoDB query - get only active session
            collection = cls.collection()
            current_time = int(time.time())
            doc = collection.find_one({
                'UserID': user_id,
                'TTL': {'$gt': current_time}
            })
            if doc:
                if '_id' in doc:
                    del doc['_id']
                return cls(**doc)
            return None
        except Exception as e:
            print(f"Error querying session by user ID: {e}")
            return None

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

    def user(self) -> Optional['Auth_Model']:
        """
        Eloquent-style relationship: Get the user for this session
        Inverse one-to-one relationship using BelongToOne

        Returns:
            Auth_Model instance or None
        """
        return belong_to_one(
            Auth_Model,
            foreign_key='UserID',
            local_key='ID'
        )(self)

    def save(self):
        """
        Save session, enforcing one-to-one constraint per user
        Deletes any existing session for the user before saving
        """
        # Hash the token if not already hashed
        if self.Token and not self._is_hashed(self.Token):
            self.Token = self._hash_token(self.Token)

        # Ensure TTL is set
        if not self.TTL:
            self.TTL = self._calculate_ttl()

        # Enforce one-to-one: Delete existing sessions for this user
        try:
            collection = self.collection()
            collection.delete_many({
                'UserID': self.UserID,
                'ID': {'$ne': self.ID}
            })
        except Exception as e:
            print(f"Warning: Could not delete old sessions: {e}")

        return super(Session_Model, self).save()
