import sys
import os
import pytest

# Add lambda-service directory to Python path FIRST
# This must happen before any imports
# Get the path to the lambda-service directory (parent of tests/)
LAMBDA_SERVICE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# Ensure the lambda-service directory is at the front of sys.path
# Remove it first if it exists elsewhere
if LAMBDA_SERVICE_PATH in sys.path:
    sys.path.remove(LAMBDA_SERVICE_PATH)
sys.path.insert(0, LAMBDA_SERVICE_PATH)

# Also set PYTHONPATH environment variable to ensure all imports work
current_pythonpath = os.environ.get('PYTHONPATH', '')
os.environ['PYTHONPATH'] = (
    LAMBDA_SERVICE_PATH + os.pathsep + current_pythonpath
)


def pytest_configure(config):
    """
    Pytest hook that runs before test collection.
    Ensures the lambda-service directory is in sys.path.
    """
    # Double-check the path is set correctly
    if LAMBDA_SERVICE_PATH not in sys.path:
        sys.path.insert(0, LAMBDA_SERVICE_PATH)
    elif sys.path[0] != LAMBDA_SERVICE_PATH:
        sys.path.remove(LAMBDA_SERVICE_PATH)
        sys.path.insert(0, LAMBDA_SERVICE_PATH)


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI application"""
    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app)


