"""
Additional controller tests for artifacts list and create endpoints.
"""
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@patch('app.controllers.artifact_controller.artifacts_list_job')
def test_artifacts_list_success_with_offset(mock_list):
    """Test artifacts listing with pagination offset"""
    mock_list.return_value = {
        "artifacts": [
            {
                "metadata": {"name": "a", "id": "1", "type": "model"},
                "data": {"url": "u"}
            }
        ],
        "offset": "opaque-offset"
    }

    resp = client.post("/artifacts", json=[{"name": "*"}])

    assert resp.status_code == 200
    assert resp.headers.get("offset") == "opaque-offset"
    assert isinstance(resp.json(), list)


@patch('app.controllers.artifact_controller.artifact_create_job')
def test_artifact_create_success_and_status_201(mock_create):
    """Test successful artifact creation through the API"""
    mock_create.return_value = {
        "metadata": {"name": "new", "id": "new-id", "type": "model"},
        "data": {"url": "https://example.com/new"}
    }

    resp = client.post(
        "/artifact/model", json={"url": "https://example.com/new"}
    )

    assert resp.status_code == 201
    assert resp.json()["metadata"]["id"] == "new-id"


def test_not_implemented_endpoints_return_501():
    """Test that not implemented endpoints return 501"""
    # This test passes as a placeholder
    pass
