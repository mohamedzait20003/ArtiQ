import json
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from src.main import app, artifact_controller


client = TestClient(app)


def make_payload(obj):
    m = Mock()
    # Payload.read() should return a JSON string
    m.read = Mock(return_value=json.dumps(obj))
    return m


def test_artifact_retrieve_success():
    # Arrange: mock lambda invoke to return a successful artifact
    artifact = {
        "metadata": {"name": "test", "id": "id-123", "type": "model"},
        "data": {"url": "https://example.com/model"}
    }
    artifact_controller.lambda_client = Mock()
    artifact_controller.lambda_client.invoke.return_value = {
        "StatusCode": 200,
        "Payload": make_payload(artifact)
    }

    # Act
    resp = client.get("/artifacts/model/id-123")

    # Assert
    assert resp.status_code == 200
    body = resp.json()
    assert body["metadata"]["id"] == "id-123" or body.get("metadata", {}).get("id") == "id-123"


def test_artifact_retrieve_lambda_json_error_propagates_status():
    # Arrange: lambda returns an errorMessage which is JSON-encoded with statusCode
    error = {"statusCode": 404, "errorMessage": "Not found"}
    artifact_controller.lambda_client = Mock()
    artifact_controller.lambda_client.invoke.return_value = {
        "StatusCode": 200,
        "Payload": make_payload({"errorMessage": json.dumps(error)})
    }

    # Act
    resp = client.get("/artifacts/model/missing-id")

    # Assert
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Not found"


def test_artifact_update_lambda_json_error_propagates_400():
    # Arrange: lambda returns a 400 error encoded in errorMessage
    error = {"statusCode": 400, "errorMessage": "Bad request"}
    artifact_controller.lambda_client = Mock()
    artifact_controller.lambda_client.invoke.return_value = {
        "StatusCode": 200,
        "Payload": make_payload({"errorMessage": json.dumps(error)})
    }

    payload = {
        "metadata": {"name": "test", "id": "id-123", "type": "model"},
        "data": {"url": "https://example.com/model"}
    }

    # Act
    resp = client.put("/artifacts/model/id-123", json=payload)

    # Assert
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Bad request"


def test_artifact_delete_lambda_json_error_propagates_404():
    # Arrange: lambda returns a 404 error encoded in errorMessage
    error = {"statusCode": 404, "errorMessage": "Not found"}
    artifact_controller.lambda_client = Mock()
    artifact_controller.lambda_client.invoke.return_value = {
        "StatusCode": 200,
        "Payload": make_payload({"errorMessage": json.dumps(error)})
    }

    # Act
    resp = client.delete("/artifacts/model/id-xyz")

    # Assert
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Not found"


def test_artifact_retrieve_non_json_error_message_returns_500():
    # Lambda returns errorMessage as plain text (not JSON) -> should map to 500
    artifact_controller.lambda_client = Mock()
    artifact_controller.lambda_client.invoke.return_value = {
        "StatusCode": 200,
        "Payload": make_payload({"errorMessage": "plain text error"})
    }

    resp = client.get("/artifacts/model/whatever")
    assert resp.status_code == 500
    assert resp.json()["detail"] == "plain text error"


def test_artifact_retrieve_statuscode_non_200_without_error_message():
    # Lambda returns non-200 StatusCode and no errorMessage -> controller should
    # return the same status code with generic detail
    artifact_controller.lambda_client = Mock()
    artifact_controller.lambda_client.invoke.return_value = {
        "StatusCode": 502,
        "Payload": make_payload({})
    }

    resp = client.get("/artifacts/model/whatever")
    assert resp.status_code == 502
    assert resp.json()["detail"] == "Lambda function execution failed"


def test_artifact_update_non_json_error_message_returns_500():
    artifact_controller.lambda_client = Mock()
    artifact_controller.lambda_client.invoke.return_value = {
        "StatusCode": 200,
        "Payload": make_payload({"errorMessage": "update failed plain"})
    }

    payload = {
        "metadata": {"name": "x", "id": "i", "type": "model"},
        "data": {"url": "https://example.com"}
    }
    resp = client.put("/artifacts/model/i", json=payload)
    assert resp.status_code == 500
    assert resp.json()["detail"] == "update failed plain"


def test_artifact_update_statuscode_non_200_without_error_message():
    artifact_controller.lambda_client = Mock()
    artifact_controller.lambda_client.invoke.return_value = {
        "StatusCode": 503,
        "Payload": make_payload({})
    }

    payload = {
        "metadata": {"name": "x", "id": "i", "type": "model"},
        "data": {"url": "https://example.com"}
    }
    resp = client.put("/artifacts/model/i", json=payload)
    assert resp.status_code == 503
    assert resp.json()["detail"] == "Lambda function execution failed"


def test_artifact_delete_non_json_error_message_returns_500():
    artifact_controller.lambda_client = Mock()
    artifact_controller.lambda_client.invoke.return_value = {
        "StatusCode": 200,
        "Payload": make_payload({"errorMessage": "delete failed plain"})
    }

    resp = client.delete("/artifacts/model/to-delete")
    assert resp.status_code == 500
    assert resp.json()["detail"] == "delete failed plain"


def test_artifact_delete_statuscode_non_200_without_error_message():
    artifact_controller.lambda_client = Mock()
    artifact_controller.lambda_client.invoke.return_value = {
        "StatusCode": 504,
        "Payload": make_payload({})
    }

    resp = client.delete("/artifacts/model/to-delete")
    assert resp.status_code == 504
    assert resp.json()["detail"] == "Lambda function execution failed"
