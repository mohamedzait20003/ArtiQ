"""
Database setup script for S3 buckets.

Run this script to set up the required S3 resources for the Model Registry.
"""
import boto3
from botocore.exceptions import ClientError
import json
from typing import Dict, Any, Optional


def create_s3_bucket(bucket_name: str, region: Optional[str] = None) -> bool:
    """
    Create an S3 bucket for storing model files.
    
    Args:
        bucket_name: Name of the bucket
        region: AWS region (defaults to boto3 default region)
        
    Returns:
        True if successful, False otherwise
    """
    # Get the actual region from boto3 session
    if region is None:
        session = boto3.Session()
        region = session.region_name or "us-east-1"
    
    s3_client = boto3.client("s3", region_name=region)
    
    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} already exists")
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] != "404":
            print(f"Error checking bucket: {e}")
            return False
    
    try:
        # Only specify LocationConstraint for non-us-east-1 regions
        if region == "us-east-1":
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region}
            )
        print(f"Bucket {bucket_name} created successfully in region {region}")
        
        # Set versioning
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={"Status": "Enabled"}
        )
        
        # Set up CORS for web uploads
        cors_config = {
            "CORSRules": [
                {
                    "AllowedHeaders": ["*"],
                    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
                    "AllowedOrigins": ["*"],
                    "MaxAgeSeconds": 3000
                }
            ]
        }
        s3_client.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_config)
        
        # Note: Public bucket policies are blocked by AWS by default
        # For production, configure bucket policies through IAM if needed
        
        return True
    except ClientError as e:
        print(f"Error creating bucket {bucket_name}: {e}")
        return False


def setup_s3_buckets(config_file: str = "s3_config.json"):
    """
    Set up all required S3 buckets.
    
    Args:
        config_file: Path to S3 configuration file
    """
    # Load configuration
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Configuration file {config_file} not found. Using defaults.")
        config = get_default_config()
    
    # Create S3 buckets
    buckets = config.get("buckets", [])
    for bucket_config in buckets:
        if isinstance(bucket_config, str):
            bucket_name = bucket_config
            region = None
        else:
            bucket_name = bucket_config["name"]
            region = bucket_config.get("region")  # None means use default
        
        create_s3_bucket(bucket_name, region)


def get_default_config() -> Dict[str, Any]:
    """Return default S3 configuration."""
    return {
        "buckets": [
            {
                "name": "ece30816-model-registry",
                "region": None  # Use boto3 default
            },
            {
                "name": "ece30816-model-evaluations",
                "region": None  # Use boto3 default
            }
        ]
    }


if __name__ == "__main__":
    setup_s3_buckets()
