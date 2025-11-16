import os
import sys
import json
from unittest.mock import Mock, patch

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


class TestArtifactUpdateLambda:
    """Unit tests for artifact_update lambda function"""

    @patch("src.lambda_functions.artifact_update.Artifact_Model")
    def test_update_success(self, mock_artifact_model):
        """Happy path: update succeeds and returns updated metadata/data"""

        from src.lambda_functions.artifact_update import lambda_handler

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

        result = lambda_handler(event, None)

        assert result["metadata"]["id"] == "abc-123"
        assert result["metadata"]["name"] == "test-model"
        assert result["metadata"]["type"] == "model"
        assert result["data"]["url"] == "https://huggingface.co/new"

        # Ensure save was attempted
        assert mock_artifact.save.called

    def test_update_name_id_mismatch_400(self):
        """Name and id mismatch should raise a 400-style exception per spec."""

        from src.lambda_functions.artifact_update import lambda_handler

        # Send metadata.id that doesn't match the path id to trigger 400
        event = {
            "artifact_type": "model",
            "id": "abc-123",
            "artifact": {
                "metadata": {"id": "different-id", "name": "different-name"},
                "data": {"url": "https://huggingface.co/new"},
            },
        }

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 400

    @patch("src.lambda_functions.artifact_update.Artifact_Model")
    def test_update_internal_error_500(self, mock_artifact_model):
        """If something unexpected happens, it should be wrapped as a 500."""

        from src.lambda_functions.artifact_update import lambda_handler

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

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 500
        assert "Error updating artifact" in err["errorMessage"]

    def test_update_invalid_type_400(self):
        """Providing an invalid artifact_type should return 400"""

        from src.lambda_functions.artifact_update import lambda_handler

        event = {
            "artifact_type": "badtype",
            "id": "abc-123",
            "artifact": {"metadata": {"id": "abc-123", "name": "test-model"}, "data": {"url": "u"}},
        }

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 400

    def test_update_invalid_id_format_400(self):
        from src.lambda_functions.artifact_update import lambda_handler

        event = {
            "artifact_type": "model",
            "id": "bad id",
            "artifact": {"metadata": {"id": "bad id", "name": "test-model"}, "data": {"url": "u"}},
        }

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 400

    @patch("src.lambda_functions.artifact_update.Artifact_Model")
    def test_update_missing_metadata_name_400(self, mock_artifact_model):
        from src.lambda_functions.artifact_update import lambda_handler

        event = {
            "artifact_type": "model",
            "id": "abc-123",
            "artifact": {"metadata": {"id": "abc-123"}, "data": {"url": "u"}},
        }

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 400

    @patch("src.lambda_functions.artifact_update.Artifact_Model")
    def test_update_artifact_not_found_404(self, mock_artifact_model):
        from src.lambda_functions.artifact_update import lambda_handler

        mock_artifact_model.get.return_value = None

        event = {
            "artifact_type": "model",
            "id": "abc-123",
            "artifact": {"metadata": {"id": "abc-123", "name": "test-model"}, "data": {"url": "u"}},
        }

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 404

    @patch("src.lambda_functions.artifact_update.Artifact_Model")
    def test_update_type_mismatch_400(self, mock_artifact_model):
        from src.lambda_functions.artifact_update import lambda_handler

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
            "artifact": {"metadata": {"id": "abc-123", "name": "test-model"}, "data": {"url": "u"}},
        }

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 400

    @patch("src.lambda_functions.artifact_update.Artifact_Model")
    def test_update_name_mismatch_400(self, mock_artifact_model):
        from src.lambda_functions.artifact_update import lambda_handler

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
            "artifact": {"metadata": {"id": "abc-123", "name": "different-name"}, "data": {"url": "u"}},
        }

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 400

    @patch("src.lambda_functions.artifact_update.Artifact_Model")
    def test_update_save_failure_500(self, mock_artifact_model):
        from src.lambda_functions.artifact_update import lambda_handler

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
            "artifact": {"metadata": {"id": "abc-123", "name": "test-model"}, "data": {"url": "u"}},
        }

        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)

        err = json.loads(str(excinfo.value))
        assert err["statusCode"] == 500
        assert "Failed to update artifact" in err["errorMessage"]
