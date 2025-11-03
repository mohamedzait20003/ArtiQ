import sys
import os
import pytest

# Add lambda-service to Python path
lambda_service_path = os.path.join(
    os.path.dirname(__file__),
    '../services/lambda-service'
)
sys.path.insert(0, lambda_service_path)


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI application"""
    from fastapi.testclient import TestClient
    from src.main import app
    
    return TestClient(app)
