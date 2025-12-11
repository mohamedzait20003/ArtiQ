from unittest.mock import Mock, patch


class TestArtifactDeleteLambda:
    """Unit tests for artifact_delete lambda function"""

    @patch("app.jobs.artifact_delete.Artifact_Model")
    def test_delete_success(self, mock_artifact_model):
        """Happy path: delete succeeds and returns a success message."""

        from app.jobs.artifact_delete import lambda_handler

        mock_artifact_instance = Mock()
        # ensure artifact_type and id match expected values so the lambda's
        # type check passes
        mock_artifact_instance.id = "abc-123"
        mock_artifact_instance.artifact_type = "model"
        mock_artifact_instance.delete.return_value = True

        # Lambda will call Artifact_Model.get(...)
        mock_artifact_model.get.return_value = mock_artifact_instance

        event = {"artifact_type": "model", "id": "abc-123"}

        result, status_code = lambda_handler(event, None)

        # The lambda returns a simple message dict on success
        assert status_code == 200
        assert isinstance(result, dict)
        assert "message" in result and "deleted" in result["message"].lower()

        mock_artifact_instance.delete.assert_called_once()

    @patch("app.jobs.artifact_delete.Artifact_Model")
    def test_delete_artifact_not_found_404(self, mock_artifact_model):
        """If artifact is not found, expect a 404 error."""

        from app.jobs.artifact_delete import lambda_handler

        # Simulate not found
        mock_artifact_model.get.return_value = None

        event = {"artifact_type": "model", "id": "does-not-exist"}

        result, status_code = lambda_handler(event, None)

        assert status_code == 404
        assert "errorMessage" in result

    def test_delete_missing_fields_400(self):
        """Missing id or artifact_type should return a 400."""

        from app.jobs.artifact_delete import lambda_handler

        event = {"id": "abc-123"}  # artifact_type intentionally omitted

        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert "errorMessage" in result

    @patch("app.jobs.artifact_delete.Artifact_Model")
    def test_delete_invalid_type_value_400(self, mock_artifact_model):
        """Providing an invalid artifact_type value should return 400"""

        from app.jobs.artifact_delete import lambda_handler

        event = {"artifact_type": "invalid", "id": "abc123"}

        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert "errorMessage" in result

    def test_delete_invalid_id_format_400(self):
        """IDs with invalid characters should return 400"""

        from app.jobs.artifact_delete import lambda_handler

        event = {"artifact_type": "model", "id": "bad id!"}

        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert "errorMessage" in result

    @patch("app.jobs.artifact_delete.Artifact_Model")
    def test_delete_type_mismatch_400(self, mock_artifact_model):
        """If the stored artifact type doesn't match the request, return 400"""

        from app.jobs.artifact_delete import lambda_handler

        mock_artifact = Mock()
        mock_artifact.id = "abc"
        mock_artifact.artifact_type = "dataset"
        mock_artifact.delete.return_value = True

        mock_artifact_model.get.return_value = mock_artifact

        event = {"artifact_type": "model", "id": "abc"}

        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert "errorMessage" in result

    @patch("app.jobs.artifact_delete.Artifact_Model")
    def test_delete_failure_returns_500(self, mock_artifact_model):
        """If artifact.delete() returns False, lambda should return 500"""

        from app.jobs.artifact_delete import lambda_handler

        mock_artifact = Mock()
        mock_artifact.id = "abc"
        mock_artifact.artifact_type = "model"
        mock_artifact.delete.return_value = False

        mock_artifact_model.get.return_value = mock_artifact

        event = {"artifact_type": "model", "id": "abc"}

        result, status_code = lambda_handler(event, None)

        assert status_code == 500
        assert "errorMessage" in result
