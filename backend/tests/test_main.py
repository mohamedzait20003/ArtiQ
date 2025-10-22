import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_healthz():
    """Test the health check endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_app_title():
    """Test that the app has the correct title"""
    assert app.title == "Serverless FastAPI"
    assert app.version == "0.1.0"
