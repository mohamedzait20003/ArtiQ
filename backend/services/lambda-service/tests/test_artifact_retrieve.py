import json
from unittest.mock import Mock, patch

import pytest


class TestArtifactRetrieveLambda:
    """Unit tests for artifact_retrieve lambda function"""

    @patch("app.jobs.artifact_retrieve.Artifact_Model")
    def test_retrieve_success(self, mock_artifact_model):
        """Happy path: artifact is found and returned"""

        from app.jobs.artifact_retrieve import lambda_handler

        # Mock the model / lookup
        mock_artifact = Mock()
        mock_artifact.id = "abc-123"
        mock_artifact.name = "test-model"
        mock_artifact.artifact_type = "model"
        mock_artifact.source_url = "https://huggingface.co/test"

        # Lambda calls Artifact_Model.get(...)
        mock_artifact_model.get.return_value = mock_artifact

        event = {"artifact_type": "model", "id": "abc-123"}

        result, status_code = lambda_handler(event, None)

        # Check status code
        assert status_code == 200
        # Basic shape checks
        assert result["metadata"]["id"] == "abc-123"
        assert result["metadata"]["name"] == "test-model"
        assert result["metadata"]["type"] == "model"
        assert result["data"]["url"] == "https://huggingface.co/test"

        mock_artifact_model.get.assert_called_once_with(
            {"id": "abc-123"}, load_s3_data=False
        )

    @patch("app.jobs.artifact_retrieve.Artifact_Model")
    def test_retrieve_not_found_404(self, mock_artifact_model):
        """
        If the artifact is not found,
        handler should raise a 404 error (wrapped in JSON).
        """

        from app.jobs.artifact_retrieve import lambda_handler

        mock_artifact_model.get.return_value = None

        event = {"artifact_type": "model", "id": "missing-id"}

        result, status_code = lambda_handler(event, None)

        assert status_code == 404
        assert "errorMessage" in result

    def test_retrieve_missing_fields_400(self):
        """
        If required fields are missing,
        handler should return a 400 error.
        """

        from app.jobs.artifact_retrieve import lambda_handler

        event = {"id": "abc-123"}  # artifact_type missing

        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert "errorMessage" in result

    def test_retrieve_invalid_type_value_400(self):
        """Providing an invalid artifact_type should return 400"""

        from app.jobs.artifact_retrieve import lambda_handler

        event = {"artifact_type": "badtype", "id": "abc-123"}

        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert "errorMessage" in result

    def test_retrieve_invalid_id_format_400(self):
        from app.jobs.artifact_retrieve import lambda_handler

        event = {"artifact_type": "model", "id": "bad id"}

        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert "errorMessage" in result

    @patch("app.jobs.artifact_retrieve.Artifact_Model")
    def test_retrieve_type_mismatch_400(self, mock_artifact_model):
        from app.jobs.artifact_retrieve import lambda_handler

        mock_artifact = Mock()
        mock_artifact.id = "abc"
        mock_artifact.name = "n"
        mock_artifact.artifact_type = "dataset"
        mock_artifact.source_url = "u"

        mock_artifact_model.get.return_value = mock_artifact

        event = {"artifact_type": "model", "id": "abc"}

        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert "errorMessage" in result
