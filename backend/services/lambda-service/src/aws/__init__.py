"""
AWS Package

Provides centralized AWS service configurations and utilities.
"""

from .config import s3_client, dynamodb, bedrock_runtime, AWS_REGION

__all__ = [
    "s3_client",
    "dynamodb",
    "bedrock_runtime",
    "AWS_REGION",
]
