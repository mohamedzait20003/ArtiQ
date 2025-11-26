"""
AWS Service Provider
Singleton AWS service instances for DynamoDB and S3
"""

import os
import boto3
from typing import Optional


class AWSServices:
    """
    AWS Services Singleton
    Provides shared DynamoDB and S3 client instances
    """

    _instance: Optional['AWSServices'] = None
    _dynamodb = None
    _s3 = None
    _lambda_client = None
    _region = None

    def __new__(cls):
        """Ensure AWSServices is a singleton"""
        if cls._instance is None:
            cls._instance = super(AWSServices, cls).__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls, region: str = None):
        """
        Initialize AWS services with specified region
        Args:
            region: AWS region (defaults to environment variable or us-east-2)
        """
        if cls._region is None:
            cls._region = region or os.environ.get('AWS_REGION', 'us-east-2')
            os.environ.setdefault('AWS_REGION', cls._region)

    @classmethod
    def get_dynamodb(cls):
        """
        Get shared DynamoDB resource instance
        Returns:
            boto3 DynamoDB resource
        """
        if cls._dynamodb is None:
            cls.initialize()
            cls._dynamodb = boto3.resource('dynamodb', region_name=cls._region)
        return cls._dynamodb

    @classmethod
    def get_s3(cls):
        """
        Get shared S3 client instance
        Returns:
            boto3 S3 client
        """
        if cls._s3 is None:
            cls.initialize()
            cls._s3 = boto3.client('s3', region_name=cls._region)
        return cls._s3

    @classmethod
    def get_lambda(cls):
        """
        Get shared Lambda client instance
        Returns:
            boto3 Lambda client
        """
        if cls._lambda_client is None:
            cls.initialize()
            cls._lambda_client = boto3.client('lambda',
                                              region_name=cls._region)
        return cls._lambda_client

    @classmethod
    def reset(cls):
        """Reset all clients (useful for testing)"""
        cls._dynamodb = None
        cls._s3 = None
        cls._lambda_client = None
        cls._region = None


# Convenience functions for easy access
def get_dynamodb():
    """Get DynamoDB resource instance"""
    return AWSServices.get_dynamodb()


def get_s3():
    """Get S3 client instance"""
    return AWSServices.get_s3()


def get_lambda():
    """Get Lambda client instance"""
    return AWSServices.get_lambda()
