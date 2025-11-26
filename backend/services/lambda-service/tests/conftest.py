import sys
import os
import pytest

# Add lambda-service directory to Python path
# This allows 'lib' and 'app' imports to work
lambda_service_path = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.insert(0, lambda_service_path)


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI application"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    return TestClient(app)
