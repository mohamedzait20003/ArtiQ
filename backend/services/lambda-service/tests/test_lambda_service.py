import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test the health check endpoint returns 200 and correct response."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}