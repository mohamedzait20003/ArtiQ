import sys
import os

# Add lambda-service directory to Python path FIRST
# This must happen before any imports
# Get the path to the lambda-service directory (parent of tests/)
lambda_service_path = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# Ensure the lambda-service directory is at the front of sys.path
# Remove it first if it exists elsewhere
if lambda_service_path in sys.path:
    sys.path.remove(lambda_service_path)
sys.path.insert(0, lambda_service_path)

# Now import pytest after path is set
import pytest  # noqa: E402


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI application"""
    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app)
