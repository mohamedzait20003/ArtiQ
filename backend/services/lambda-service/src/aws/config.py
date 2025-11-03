import os
import boto3


# Get AWS configuration from environment variables
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")


def _get_boto3_config():
    """
    Build boto3 configuration dictionary

    Returns:
        dict: Configuration for boto3 clients/resources
    """
    config = {"region_name": AWS_REGION}

    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        config.update({
            "aws_access_key_id": AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": AWS_SECRET_ACCESS_KEY
        })

    return config


s3_client = boto3.client("s3", **_get_boto3_config())
dynamodb = boto3.resource("dynamodb", **_get_boto3_config())
bedrock_runtime = boto3.client("bedrock-runtime", **_get_boto3_config())


# Export for use throughout the application
__all__ = [
    "s3_client",
    "dynamodb",
    "bedrock_runtime",
    "AWS_REGION",
]
