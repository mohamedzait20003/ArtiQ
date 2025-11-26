from unittest.mock import patch


class TestRegistryResetLambda:
    """Unit tests for registry_reset lambda function"""

    @patch('app.models.Auth_Model.Auth_Model.table')
    @patch('app.models.Session_Model.Session_Model.table')
    @patch('app.models.Artifact_Model.Artifact_Model.scan_artifacts')
    def test_lambda_handler_success(
            self, mock_scan, mock_session_table, mock_auth_table):
        """Test successful registry reset"""
        from app.jobs.registry_reset import lambda_handler

        # Mock empty artifact scan
        mock_scan.return_value = {
            'items': [],
            'last_evaluated_key': None
        }

        # Mock empty session table scan
        mock_session_table.return_value.scan.return_value = {'Items': []}

        # Mock empty auth table scan
        mock_auth_table.return_value.scan.return_value = {'Items': []}

        event = {
            'X-Authorization': 'test-token',
            'ARTIFACTS_BUCKET': 'test-bucket'
        }

        result = lambda_handler(event, None)

        assert result['statusCode'] == 200
        # Match actual message
        assert 'Registry is reset.' in result['body']

    @patch('app.models.Artifact_Model.Artifact_Model.scan_artifacts')
    def test_lambda_handler_dynamo_error(self, mock_scan):
        """Test registry reset with DynamoDB error"""
        from app.jobs.registry_reset import lambda_handler

        # Mock scan to raise exception
        mock_scan.side_effect = Exception("DynamoDB scan error")

        event = {
            'X-Authorization': 'test-token',
            'ARTIFACTS_BUCKET': 'test-bucket'
        }

        result = lambda_handler(event, None)

        assert result['statusCode'] == 500
        assert 'error' in result['body']
        assert 'DynamoDB scan error' in result['body']
