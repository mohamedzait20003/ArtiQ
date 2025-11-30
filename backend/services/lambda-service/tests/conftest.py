import os
import sys

import boto3
import pytest
import mongomock
from fastapi.testclient import TestClient
from moto import mock_aws

# Configure AWS credentials before any boto3 imports
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_SECURITY_TOKEN'] = 'testing'
os.environ['AWS_SESSION_TOKEN'] = 'testing'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-2'
# Set mock MongoDB URI to prevent real connection attempts
os.environ.setdefault('MONGODB_URI', 'mongodb://mock:27017/')

# Add lambda-service directory to Python path
LAMBDA_SERVICE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if LAMBDA_SERVICE_PATH not in sys.path:
    sys.path.insert(0, LAMBDA_SERVICE_PATH)

# Add backend root to Python path for lib imports
BACKEND_ROOT = os.path.dirname(os.path.dirname(LAMBDA_SERVICE_PATH))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.main import app  # noqa: E402
from lib.aws import AWSServices  # noqa: E402


def pytest_configure(config):
    """Pytest hook that runs before test collection."""
    if LAMBDA_SERVICE_PATH not in sys.path:
        sys.path.insert(0, LAMBDA_SERVICE_PATH)
    if BACKEND_ROOT not in sys.path:
        sys.path.insert(0, BACKEND_ROOT)


@pytest.fixture(scope="function", autouse=True)
def aws_resources():
    """
    Setup mocked AWS resources for all tests.
    Creates MongoDB collections and S3 buckets needed for testing.
    """
    with mock_aws():
        # Create mock MongoDB client
        mongo_client = mongomock.MongoClient()
        test_db = mongo_client['docdb-ece30861-project']
        
        # Override AWSServices to use mock MongoDB
        AWSServices._documentdb_client = mongo_client
        AWSServices._documentdb_database = test_db
        
        # Create collections (MongoDB equivalent of tables)
        test_db.create_collection('Artifacts')
        test_db.create_collection('Sessions')
        test_db.create_collection('Users')
        test_db.create_collection('Roles')
        test_db.create_collection('dummy-table')
        
        # Create indexes for MongoDB collections
        test_db['Sessions'].create_index('token', unique=True)
        test_db['Users'].create_index('Username', unique=True)
        test_db['Users'].create_index('Email', unique=True)
        test_db['Roles'].create_index('Name', unique=True)
        test_db['Artifacts'].create_index('ID', unique=True)
        test_db['Artifacts'].create_index('Name')

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
        
        # Cleanup
        AWSServices.reset()


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)
