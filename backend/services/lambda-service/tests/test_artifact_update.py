import json
from unittest.mock import Mock, patch

import pytest


class TestArtifactUpdateLambda:
    """Unit tests for artifact_update lambda function"""

    @patch("app.jobs.artifact_update.Artifact_Model")
    def test_update_success(self, mock_artifact_model):
        """Happy path: update succeeds and returns updated metadata/data"""

        from app.jobs.artifact_update import lambda_handler

        # Mock existing artifact instance
        mock_artifact = Mock()
        mock_artifact.id = "abc-123"
        mock_artifact.name = "test-model"
        mock_artifact.artifact_type = "model"
        mock_artifact.source_url = "https://huggingface.co/old"
        mock_artifact.save.return_value = True

        # Lambda looks up existing artifact with Artifact_Model.get(...)
        mock_artifact_model.get.return_value = mock_artifact

        # Lambda expects nested artifact with metadata and data
        event = {
            "artifact_type": "model",
            "id": "abc-123",
            "artifact": {
                "metadata": {"id": "abc-123", "name": "test-model"},
                "data": {"url": "https://huggingface.co/new"},
            },
        }

        result, status_code = lambda_handler(event, None)

        assert status_code == 200
        assert result["metadata"]["id"] == "abc-123"
        assert result["metadata"]["name"] == "test-model"
        assert result["metadata"]["type"] == "model"
        assert result["data"]["url"] == "https://huggingface.co/new"

        # Ensure save was attempted
        assert mock_artifact.save.called

    def test_update_name_id_mismatch_400(self):
        """Name and id mismatch should return a 400 status code."""

        from app.jobs.artifact_update import lambda_handler

        # Send metadata.id that doesn't match the path id to trigger 400
        event = {
            "artifact_type": "model",
            "id": "abc-123",
            "artifact": {
                "metadata": {"id": "different-id", "name": "different-name"},
                "data": {"url": "https://huggingface.co/new"},
            },
        }

        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert "errorMessage" in result

    @patch("app.jobs.artifact_update.Artifact_Model")
    def test_update_internal_error_500(self, mock_artifact_model):
        """If something unexpected happens, it should return a 500 status code."""

        from app.jobs.artifact_update import lambda_handler

        # Simulate an unexpected error during lookup
        mock_artifact_model.get.side_effect = RuntimeError("boom")

        event = {
            "artifact_type": "model",
            "id": "abc-123",
            "artifact": {
                "metadata": {"id": "abc-123", "name": "test-model"},
                "data": {"url": "https://huggingface.co/new"},
            },
        }

        result, status_code = lambda_handler(event, None)

        assert status_code == 500
        assert "errorMessage" in result
        assert "Error updating artifact" in result["errorMessage"]

    def test_update_invalid_type_400(self):
        """Providing an invalid artifact_type should return 400"""

        from app.jobs.artifact_update import lambda_handler

        event = {
            "artifact_type": "badtype",
            "id": "abc-123",
            "artifact": {
                "metadata": {"id": "abc-123", "name": "test-model"},
                "data": {"url": "u"}
            },
        }

        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert "errorMessage" in result

    def test_update_invalid_id_format_400(self):
        from app.jobs.artifact_update import lambda_handler

        event = {
            "artifact_type": "model",
            "id": "bad id",
            "artifact": {
                "metadata": {"id": "bad id", "name": "test-model"},
                "data": {"url": "u"}
            },
        }

        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert "errorMessage" in result

    @patch("app.jobs.artifact_update.Artifact_Model")
    def test_update_missing_metadata_name_400(self, mock_artifact_model):
        from app.jobs.artifact_update import lambda_handler

        event = {
            "artifact_type": "model",
            "id": "abc-123",
            "artifact": {"metadata": {"id": "abc-123"}, "data": {"url": "u"}},
        }

        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert "errorMessage" in result

    @patch("app.jobs.artifact_update.Artifact_Model")
    def test_update_artifact_not_found_404(self, mock_artifact_model):
        from app.jobs.artifact_update import lambda_handler

        mock_artifact_model.get.return_value = None

        event = {
            "artifact_type": "model",
            "id": "abc-123",
            "artifact": {
                "metadata": {"id": "abc-123", "name": "test-model"},
                "data": {"url": "u"}
            },
        }

        result, status_code = lambda_handler(event, None)

        assert status_code == 404
        assert "errorMessage" in result

    @patch("app.jobs.artifact_update.Artifact_Model")
    def test_update_type_mismatch_400(self, mock_artifact_model):
        from app.jobs.artifact_update import lambda_handler

        mock_artifact = Mock()
        mock_artifact.id = "abc-123"
        mock_artifact.name = "test-model"
        mock_artifact.artifact_type = "dataset"
        mock_artifact.source_url = "u"
        mock_artifact.save.return_value = True

        mock_artifact_model.get.return_value = mock_artifact

        event = {
            "artifact_type": "model",
            "id": "abc-123",
            "artifact": {"metadata": {"id": "abc-123", "name": "test-model"},
                         "data": {"url": "u"}},
        }

        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert "errorMessage" in result

    @patch("app.jobs.artifact_update.Artifact_Model")
    def test_update_name_mismatch_400(self, mock_artifact_model):
        from app.jobs.artifact_update import lambda_handler

        mock_artifact = Mock()
        mock_artifact.id = "abc-123"
        mock_artifact.name = "existing-name"
        mock_artifact.artifact_type = "model"
        mock_artifact.source_url = "u"
        mock_artifact.save.return_value = True

        mock_artifact_model.get.return_value = mock_artifact

        event = {
            "artifact_type": "model",
            "id": "abc-123",
            "artifact": {
                "metadata": {
                    "id": "abc-123",
                    "name": "different-name"
                },
                "data": {"url": "u"}
            },
        }

        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert "errorMessage" in result

    @patch("app.jobs.artifact_update.Artifact_Model")
    def test_update_save_failure_500(self, mock_artifact_model):
        from app.jobs.artifact_update import lambda_handler

        mock_artifact = Mock()
        mock_artifact.id = "abc-123"
        mock_artifact.name = "test-model"
        mock_artifact.artifact_type = "model"
        mock_artifact.source_url = "u"
        mock_artifact.save.return_value = False

        mock_artifact_model.get.return_value = mock_artifact

        event = {
            "artifact_type": "model",
            "id": "abc-123",
            "artifact": {
                "metadata": {"id": "abc-123", "name": "test-model"},
                "data": {"url": "u"}
            },
        }

        result, status_code = lambda_handler(event, None)

        assert status_code == 500
        assert "errorMessage" in result
        assert "Failed to update artifact" in result["errorMessage"]
