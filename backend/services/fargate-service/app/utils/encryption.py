"""
Encryption utilities for Fargate service
Provides functions to decrypt artifact IDs
"""
from include import decrypt_artifact_id as lib_decrypt_artifact_id


def decrypt_artifact_id(encrypted_artifact_id: str) -> str:
    """
    Decrypt an encrypted artifact ID

    Args:
        encrypted_artifact_id: The encrypted artifact ID string

    Returns:
        str: The decrypted artifact ID

    Raises:
        ValueError: If decryption fails
        Exception: If other errors occur during decryption
    """
    try:
        decrypted_id = lib_decrypt_artifact_id(encrypted_artifact_id)
        return decrypted_id
    except ValueError as e:
        raise ValueError(f"Failed to decrypt artifact ID: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error during decryption: {str(e)}")
