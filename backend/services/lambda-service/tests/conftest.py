import sys
import os
import pytest

# Add lambda-service directory to Python path
# This allows 'lib' and 'app' imports to work
# Get the path to the lambda-service directory (parent of tests/)
lambda_service_path = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# Ensure the lambda-service directory is first in sys.path
# This is crucial for both local and CI/CD environments
if lambda_service_path not in sys.path:
    sys.path.insert(0, lambda_service_path)
elif sys.path[0] != lambda_service_path:
    sys.path.remove(lambda_service_path)
    sys.path.insert(0, lambda_service_path)


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI application"""
    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app)
