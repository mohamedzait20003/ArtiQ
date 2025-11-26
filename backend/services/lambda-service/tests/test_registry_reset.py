import sys
import os
from unittest.mock import Mock, patch

# Ensure src is importable
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app'))
)


class TestRegistryResetLambda:
    """Unit tests for registry_reset lambda function"""

    @patch('app.jobs.registry_reset.s3_client')
    @patch('app.jobs.registry_reset.dynamodb')
    def test_lambda_handler_success(self, mock_dynamodb, mock_s3_client):
        """Test successful registry reset"""
        from app.jobs.registry_reset import lambda_handler

        # Mock DynamoDB table
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.scan.return_value = {'Items': []}

        # Mock S3
        mock_s3_client.list_objects_v2.return_value = {'Contents': []}

        event = {
            'X-Authorization': 'test-token',
            'ARTIFACTS_BUCKET': 'test-bucket'
        }

        result = lambda_handler(event, None)

        assert result['statusCode'] == 200
        assert 'Registry is reset.' in result['body']  # Match actual message

    @patch('app.jobs.registry_reset.dynamodb')
    def test_lambda_handler_dynamo_error(self, mock_dynamodb):
        """Test registry reset with DynamoDB error"""
        from app.jobs.registry_reset import lambda_handler

        # Mock DynamoDB table to raise exception during scan
        mock_table = Mock()
        mock_table.scan.side_effect = Exception("DynamoDB scan error")
        mock_dynamodb.Table.return_value = mock_table

        event = {
            'X-Authorization': 'test-token',
            'ARTIFACTS_BUCKET': 'test-bucket'
        }

        result = lambda_handler(event, None)

        assert result['statusCode'] == 500
        assert 'error' in result['body']
        assert 'DynamoDB scan error' in result['body']
