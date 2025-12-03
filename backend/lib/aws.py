"""
AWS Service Provider
Singleton AWS service instances for DocumentDB and S3
"""

import os
import boto3
from typing import Optional
from pymongo import MongoClient


class AWSServices:
    """
    AWS Services Singleton
    Provides shared DocumentDB and S3 client instances
    """

    _instance: Optional['AWSServices'] = None
    _documentdb_client = None
    _documentdb_database = None
    _s3 = None
    _lambda_client = None
    _sqs = None
    _sqs_queue_url = None
    _region = None
    _database_name = "docdb-ece30861-project"

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
            region: AWS region (defaults to environment variable)
        """
        if cls._region is None:
            cls._region = region or os.environ.get('AWS_REGION', 'us-east-2')
            os.environ.setdefault('AWS_REGION', cls._region)

        # Initialize DocumentDB if not already initialized
        if cls._documentdb_client is None:
            cls._init_documentdb()

    @classmethod
    def _init_documentdb(cls):
        """Initialize DocumentDB/MongoDB connection"""
        # Get MongoDB URI from environment variable
        connection_string = os.environ.get(
            'MONGODB_URI',
            'mongodb://localhost:27017/'
        )

        database_name = cls._database_name        # Create MongoDB client
        cls._documentdb_client = MongoClient(
            connection_string,
            retryWrites=False,
            maxPoolSize=50,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )

        # Test connection (skip for mock URIs used in testing)
        if 'mock' not in connection_string:
            cls._documentdb_client.admin.command('ping')

        # Get database
        cls._documentdb_database = cls._documentdb_client[database_name]

        print(f"✓ Connected to MongoDB: {database_name}")

    @classmethod
    def get_documentdb(cls):
        """
        Get shared DocumentDB database instance

        Returns:
            MongoDB Database instance
        """
        if cls._documentdb_database is None:
            cls.initialize()
        return cls._documentdb_database

    @classmethod
    def get_collection(cls, collection_name: str):
        """
        Get a collection from DocumentDB

        Args:
            collection_name: Name of the collection

        Returns:
            MongoDB Collection instance
        """
        db = cls.get_documentdb()
        return db[collection_name]

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
    def get_sqs(cls):
        """
        Get shared SQS client instance
        Returns:
            boto3 SQS client
        """
        if cls._sqs is None:
            cls.initialize()
            cls._sqs = boto3.client('sqs', region_name=cls._region)
        return cls._sqs

    @classmethod
    def get_sqs_queue_url(cls):
        """
        Get the artifact processing queue URL from environment
        Returns:
            SQS queue URL string or None if not configured
        """
        if cls._sqs_queue_url is None:
            cls._sqs_queue_url = os.environ.get(
                'ARTIFACT_PROCESSING_QUEUE_URL'
            )
        return cls._sqs_queue_url

    @classmethod
    def reset(cls):
        """Reset all clients (useful for testing)"""
        if cls._documentdb_client:
            cls._documentdb_client.close()

        cls._documentdb_client = None
        cls._documentdb_database = None
        cls._s3 = None
        cls._lambda_client = None
        cls._sqs = None
        cls._sqs_queue_url = None
        cls._region = None


# Convenience functions for easy access
def get_documentdb():
    """Get DocumentDB database instance"""
    return AWSServices.get_documentdb()


def get_collection(collection_name: str):
    """Get a collection from DocumentDB"""
    return AWSServices.get_collection(collection_name)


def get_s3():
    """Get S3 client instance"""
    return AWSServices.get_s3()


def get_lambda():
    """Get Lambda client instance"""
    return AWSServices.get_lambda()


def get_sqs():
    """Get SQS client instance"""
    return AWSServices.get_sqs()


def get_sqs_queue_url():
    """Get SQS queue URL"""
    return AWSServices.get_sqs_queue_url()
