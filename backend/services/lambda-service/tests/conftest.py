import os
import sys

import boto3
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws

# Configure AWS credentials before any boto3 imports
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-2'

# Add lambda-service directory to Python path
LAMBDA_SERVICE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if LAMBDA_SERVICE_PATH not in sys.path:
    sys.path.insert(0, LAMBDA_SERVICE_PATH)

from app.main import app  # noqa: E402


def pytest_configure(config):
    """Pytest hook that runs before test collection."""
    if LAMBDA_SERVICE_PATH not in sys.path:
        sys.path.insert(0, LAMBDA_SERVICE_PATH)


@pytest.fixture(scope="function", autouse=True)
def aws_resources():
    """
    Setup mocked AWS resources for all tests.
    Creates DynamoDB tables and S3 buckets needed for testing.
    """
    with mock_aws():
        # Create DynamoDB client
        dynamodb = boto3.resource('dynamodb', region_name='us-east-2')

        # Create Artifacts table
        dynamodb.create_table(
            TableName='Artifacts',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        # Create Sessions table
        dynamodb.create_table(
            TableName='Sessions',
            KeySchema=[
                {'AttributeName': 'token', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'token', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        # Create Auth table
        dynamodb.create_table(
            TableName='Auth',
            KeySchema=[
                {'AttributeName': 'username', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'username', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        # Create dummy-table for Model tests
        dynamodb.create_table(
            TableName='dummy-table',
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        # Create S3 buckets
        s3 = boto3.client('s3', region_name='us-east-2')
        s3.create_bucket(
            Bucket='dummy-bucket',
            CreateBucketConfiguration={'LocationConstraint': 'us-east-2'}
        )
        s3.create_bucket(
            Bucket='test-artifacts-bucket',
            CreateBucketConfiguration={'LocationConstraint': 'us-east-2'}
        )
        s3.create_bucket(
            Bucket='artifacts-bucket',
            CreateBucketConfiguration={'LocationConstraint': 'us-east-2'}
        )

        yield


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)
