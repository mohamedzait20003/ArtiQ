import os
import sys
import json
from unittest.mock import Mock, patch

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


class TestArtifactRetrieveLambda:
    """Unit tests for artifact_retrieve lambda function"""

    @patch("src.lambda_functions.artifact_retrieve.Artifact_Model")
    def test_retrieve_success(self, mock_artifact_model):
        """Happy path: artifact is found and returned"""

        from src.lambda_functions.artifact_retrieve import lambda_handler

        # Mock the model / lookup
        mock_artifact = Mock()
        mock_artifact.id = "abc-123"
        mock_artifact.name = "test-model"
        mock_artifact.artifact_type = "model"
        mock_artifact.source_url = "https://huggingface.co/test"

        # Lambda calls Artifact_Model.get(...)
        mock_artifact_model.get.return_value = mock_artifact

        event = {"artifact_type": "model", "id": "abc-123"}

        result = lambda_handler(event, None)

        # Basic shape checks
        assert result["metadata"]["id"] == "abc-123"
        assert result["metadata"]["name"] == "test-model"
        assert result["metadata"]["type"] == "model"
        assert result["data"]["url"] == "https://huggingface.co/test"

        mock_artifact_model.get.assert_called_once_with({"id": "abc-123"}, load_s3_data=False)

    @patch("src.lambda_functions.artifact_retrieve.Artifact_Model")
    def test_retrieve_not_found_404(self, mock_artifact_model):
        """If the artifact is not found, handler should raise a 404 error (wrapped in JSON)."""

        from src.lambda_functions.artifact_retrieve import lambda_handler

        mock_artifact_model.get.return_value = None

        event = {"artifact_type": "model", "id": "missing-id"}

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 404

    def test_retrieve_missing_fields_400(self):
        """If required fields are missing, handler should return a 400 error."""

        from src.lambda_functions.artifact_retrieve import lambda_handler

        event = {"id": "abc-123"}  # artifact_type missing

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 400

    def test_retrieve_invalid_type_value_400(self):
        """Providing an invalid artifact_type should return 400"""

        from src.lambda_functions.artifact_retrieve import lambda_handler

        event = {"artifact_type": "badtype", "id": "abc-123"}

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 400

    def test_retrieve_invalid_id_format_400(self):
        from src.lambda_functions.artifact_retrieve import lambda_handler

        event = {"artifact_type": "model", "id": "bad id"}

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 400

    @patch("src.lambda_functions.artifact_retrieve.Artifact_Model")
    def test_retrieve_type_mismatch_400(self, mock_artifact_model):
        from src.lambda_functions.artifact_retrieve import lambda_handler

        mock_artifact = Mock()
        mock_artifact.id = "abc"
        mock_artifact.name = "n"
        mock_artifact.artifact_type = "dataset"
        mock_artifact.source_url = "u"

        mock_artifact_model.get.return_value = mock_artifact

        event = {"artifact_type": "model", "id": "abc"}

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 400
