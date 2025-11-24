import os
import sys
import json
from unittest.mock import Mock, patch

import pytest

# Original combined CRUD test file — kept for history but skipped to avoid
# duplicate test collection. See the split modules:
# - test_artifact_retrieve.py
# - test_artifact_update.py
# - test_artifact_delete.py
pytest.skip("Original combined CRUD tests skipped — use split modules instead", allow_module_level=True)

def test_placeholder():
    # Placeholder so pytest has at least one test if this file accidentally runs
    assert True

import os
import sys
import json
from unittest.mock import Mock, patch

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


# ---------- artifact_retrieve lambda ----------

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


# ---------- artifact_update lambda ----------


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


# ---------- artifact_delete lambda ----------


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
