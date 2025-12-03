"""
Encryption utilities
Provides encryption/decryption functions for sensitive data
"""

import os
from cryptography.fernet import Fernet


def get_encryption_key() -> bytes:
    """
    Get encryption key from environment variable

    Returns:
        Encryption key as bytes

    Raises:
        ValueError: If encryption key is not configured
    """
    key = os.environ.get('ARTIFACT_ENCRYPTION_KEY')
    if not key:
        raise ValueError(
            "ARTIFACT_ENCRYPTION_KEY not set in environment variables"
        )
    return key.encode() if isinstance(key, str) else key


def generate_encryption_key() -> str:
    """
    Generate a new encryption key

    Returns:
        Base64-encoded encryption key as string
    """
    return Fernet.generate_key().decode()


def encrypt(data: str, key: bytes = None) -> str:
    """
    Encrypt a string using Fernet symmetric encryption

    Args:
        data: The string to encrypt
        key: Optional encryption key (uses env key if not provided)

    Returns:
        Encrypted data as base64 string
    """
    if key is None:
        key = get_encryption_key()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode())
    return encrypted.decode()


def decrypt(encrypted_data: str, key: bytes = None) -> str:
    """
    Decrypt a string using Fernet symmetric encryption

    Args:
        encrypted_data: The encrypted string (base64)
        key: Optional encryption key (uses env key if not provided)

    Returns:
        Decrypted data as string

    Raises:
        cryptography.fernet.InvalidToken: If decryption fails
    """
    if key is None:
        key = get_encryption_key()

    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_data.encode())
    return decrypted.decode()


def encrypt_artifact_id(artifact_id: str) -> str:
    """
    Encrypt artifact ID for secure transmission

    Args:
        artifact_id: The artifact ID to encrypt

    Returns:
        Encrypted artifact ID
    """
    return encrypt(artifact_id)


def decrypt_artifact_id(encrypted_id: str) -> str:
    """
    Decrypt artifact ID from secure transmission

    Args:
        encrypted_id: The encrypted artifact ID

    Returns:
        Decrypted artifact ID
    """
    return decrypt(encrypted_id)
