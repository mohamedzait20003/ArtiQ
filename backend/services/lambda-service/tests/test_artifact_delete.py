import os
import sys
import json
from unittest.mock import Mock, patch

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


class TestArtifactDeleteLambda:
    """Unit tests for artifact_delete lambda function"""

    @patch("src.lambda_functions.artifact_delete.Artifact_Model")
    def test_delete_success(self, mock_artifact_model):
        """Happy path: delete succeeds and returns a success message."""

        from src.lambda_functions.artifact_delete import lambda_handler

        mock_artifact_instance = Mock()
        # ensure artifact_type and id match expected values so the lambda's
        # type check passes
        mock_artifact_instance.id = "abc-123"
        mock_artifact_instance.artifact_type = "model"
        mock_artifact_instance.delete.return_value = True

        # Lambda will call Artifact_Model.get(...)
        mock_artifact_model.get.return_value = mock_artifact_instance

        event = {"artifact_type": "model", "id": "abc-123"}

        result = lambda_handler(event, None)

        # The lambda returns a simple message dict on success
        assert isinstance(result, dict)
        assert "message" in result and "deleted" in result["message"].lower()

        mock_artifact_instance.delete.assert_called_once()

    @patch("src.lambda_functions.artifact_delete.Artifact_Model")
    def test_delete_artifact_not_found_404(self, mock_artifact_model):
        """If artifact is not found, expect a 404 error."""

        from src.lambda_functions.artifact_delete import lambda_handler

        # Simulate not found
        mock_artifact_model.get.return_value = None

        event = {"artifact_type": "model", "id": "does-not-exist"}

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 404

    def test_delete_missing_fields_400(self):
        """Missing id or artifact_type should raise a 400."""

        from src.lambda_functions.artifact_delete import lambda_handler

        event = {"id": "abc-123"}  # artifact_type intentionally omitted

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 400

    @patch("src.lambda_functions.artifact_delete.Artifact_Model")
    def test_delete_invalid_type_value_400(self, mock_artifact_model):
        """Providing an invalid artifact_type value should return 400"""

        from src.lambda_functions.artifact_delete import lambda_handler

        event = {"artifact_type": "invalid", "id": "abc123"}

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 400

    def test_delete_invalid_id_format_400(self):
        """IDs with invalid characters should raise 400"""

        from src.lambda_functions.artifact_delete import lambda_handler

        event = {"artifact_type": "model", "id": "bad id!"}

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 400

    @patch("src.lambda_functions.artifact_delete.Artifact_Model")
    def test_delete_type_mismatch_400(self, mock_artifact_model):
        """If the stored artifact type doesn't match the request, return 400"""

        from src.lambda_functions.artifact_delete import lambda_handler

        mock_artifact = Mock()
        mock_artifact.id = "abc"
        mock_artifact.artifact_type = "dataset"
        mock_artifact.delete.return_value = True

        mock_artifact_model.get.return_value = mock_artifact

        event = {"artifact_type": "model", "id": "abc"}

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 400

    @patch("src.lambda_functions.artifact_delete.Artifact_Model")
    def test_delete_failure_returns_500(self, mock_artifact_model):
        """If artifact.delete() returns False, lambda should raise 500"""

        from src.lambda_functions.artifact_delete import lambda_handler

        mock_artifact = Mock()
        mock_artifact.id = "abc"
        mock_artifact.artifact_type = "model"
        mock_artifact.delete.return_value = False

        mock_artifact_model.get.return_value = mock_artifact

        event = {"artifact_type": "model", "id": "abc"}

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 500
