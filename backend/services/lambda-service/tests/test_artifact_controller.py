"""
Controller tests - these test the FastAPI endpoints with mocked job functions.
The job functions are tested separately in their own test files.
"""
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@patch('app.controllers.artifact_controller.artifact_retrieve_job')
def test_artifact_retrieve_success(mock_retrieve):
    """Test successful artifact retrieval through the API"""
    mock_retrieve.return_value = {
        "metadata": {"name": "test", "id": "id-123", "type": "model"},
        "data": {"url": "https://example.com/model"}
    }

    resp = client.get("/artifacts/model/id-123")

    assert resp.status_code == 200
    body = resp.json()
    assert body["metadata"]["id"] == "id-123"


@patch('app.controllers.artifact_controller.artifact_update_job')
def test_artifact_update_success(mock_update):
    """Test successful artifact update through the API"""
    mock_update.return_value = {
        "metadata": {"name": "test", "id": "id-123", "type": "model"},
        "data": {"url": "https://example.com/updated"}
    }

    payload = {
        "metadata": {"name": "test", "id": "id-123", "type": "model"},
        "data": {"url": "https://example.com/updated"}
    }

    resp = client.put("/artifacts/model/id-123", json=payload)

    assert resp.status_code == 200
    assert resp.json()["data"]["url"] == "https://example.com/updated"


@patch('app.controllers.artifact_controller.artifact_delete_job')
def test_artifact_delete_success(mock_delete):
    """Test successful artifact deletion through the API"""
    mock_delete.return_value = {"message": "Artifact deleted successfully"}

    resp = client.delete("/artifacts/model/id-123")

    assert resp.status_code == 200
    assert "deleted" in resp.json()["message"].lower()
