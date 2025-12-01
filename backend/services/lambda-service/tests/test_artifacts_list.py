import base64
import json
from unittest.mock import Mock, patch


class TestArtifactsListLambda:
    """Unit tests for artifacts_list lambda function"""

    def test_parse_offset_with_none(self):
        """Test parse_offset with None input"""
        from app.jobs.artifacts_list import parse_offset

        result = parse_offset(None)
        assert result is None

    def test_parse_offset_with_empty_string(self):
        """Test parse_offset with empty string"""
        from app.jobs.artifacts_list import parse_offset

        result = parse_offset("")
        assert result is None

    def test_parse_offset_with_valid_base64(self):
        """Test parse_offset with valid base64 encoded JSON"""
        from app.jobs.artifacts_list import parse_offset

        # Create valid test data
        test_key = {"id": "test-123", "name": "test-artifact"}
        encoded = base64.b64encode(
            json.dumps(test_key).encode('utf-8')
        ).decode('utf-8')

        result = parse_offset(encoded)
        assert result == test_key

    def test_parse_offset_with_invalid_base64(self):
        """Test parse_offset with invalid base64"""
        from app.jobs.artifacts_list import parse_offset

        result = parse_offset("invalid-base64!")
        assert result is None

    def test_encode_offset_with_none(self):
        """Test encode_offset with None input"""
        from app.jobs.artifacts_list import encode_offset

        result = encode_offset(None)
        assert result is None

    def test_encode_offset_with_valid_key(self):
        """Test encode_offset with valid MongoDB document"""
        from app.jobs.artifacts_list import encode_offset

        test_key = {"id": "test-123", "name": "test-artifact"}
        result = encode_offset(test_key)

        # Verify it's a valid base64 string
        assert isinstance(result, str)

        # Verify it can be decoded back
        decoded = base64.b64decode(result.encode('utf-8'))
        decoded_json = json.loads(decoded.decode('utf-8'))
        assert decoded_json == test_key

    def test_lambda_handler_basic_query(self):
        """Test lambda_handler with basic wildcard query"""
        from app.jobs.artifacts_list import lambda_handler

        # Mock scan_artifacts response
        mock_artifacts = [
            Mock(name="test-artifact", id="123", artifact_type="model"),
            Mock(name="another-artifact", id="456", artifact_type="dataset")
        ]

        from app.models.Artifact_Model import Artifact_Model
        with patch.object(Artifact_Model, 'scan_artifacts') as mock_scan:
            mock_scan.return_value = {
                'items': mock_artifacts,
                'last_evaluated_key': None
            }

            # Test event
            event = {
                'artifact_queries': [{'name': '*'}],
                'offset': None,
                'auth_token': 'test-token'
            }

            result, status_code = lambda_handler(event, None)

            # Verify response structure
            assert status_code == 200
            assert 'artifacts' in result
            assert 'offset' in result
            assert len(result['artifacts']) == 2
            assert result['offset'] is None

            # Verify scan was called correctly
            mock_scan.assert_called_once_with(
                name_filter='*',  # The function passes '*' directly, not None
                types_filter=None,
                limit=100,
                exclusive_start_key=None
            )

    def test_lambda_handler_with_name_filter(self):
        """Test lambda_handler with specific name filter"""
        from app.jobs.artifacts_list import lambda_handler

        mock_artifacts = [
            Mock(name="bert-base", id="123", artifact_type="model")
        ]

        from app.models.Artifact_Model import Artifact_Model
        with patch.object(Artifact_Model, 'scan_artifacts') as mock_scan:
            mock_scan.return_value = {
                'items': mock_artifacts,
                'last_evaluated_key': None
            }

            event = {
                'artifact_queries': [{'name': 'bert-base'}],
                'offset': None,
                'auth_token': 'test-token'
            }

            result, status_code = lambda_handler(event, None)

            assert status_code == 200
            assert len(result['artifacts']) == 1
            mock_scan.assert_called_once_with(
                name_filter='bert-base',
                types_filter=None,
                limit=100,
                exclusive_start_key=None
            )

    def test_lambda_handler_with_type_filter(self):
        """Test lambda_handler with type filter"""
        from app.jobs.artifacts_list import lambda_handler

        mock_artifacts = [
            Mock(name="test-model", id="123", artifact_type="model")
        ]

        from app.models.Artifact_Model import Artifact_Model
        with patch.object(Artifact_Model, 'scan_artifacts') as mock_scan:
            mock_scan.return_value = {
                'items': mock_artifacts,
                'last_evaluated_key': None
            }

            event = {
                'artifact_queries': [{'name': '*', 'types': ['model']}],
                'offset': None,
                'auth_token': 'test-token'
            }

            result, status_code = lambda_handler(event, None)

            assert status_code == 200
            assert len(result['artifacts']) == 1
            mock_scan.assert_called_once_with(
                name_filter='*',  # The function passes '*' directly, not None
                types_filter=['model'],
                limit=100,
                exclusive_start_key=None
            )

    def test_lambda_handler_with_pagination(self):
        """Test lambda_handler with pagination"""
        from app.jobs.artifacts_list import lambda_handler

        # Mock response with pagination
        mock_artifacts = [
            Mock(name=f"artifact-{i}", id=str(i), artifact_type="model")
            for i in range(100)
        ]
        next_key = {"id": "last-item-id"}

        from app.models.Artifact_Model import Artifact_Model
        with patch.object(Artifact_Model, 'scan_artifacts') as mock_scan:
            mock_scan.return_value = {
                'items': mock_artifacts,
                'last_evaluated_key': next_key
            }

            event = {
                'artifact_queries': [{'name': '*'}],
                'offset': None,
                'auth_token': 'test-token'
            }

            result, status_code = lambda_handler(event, None)

            assert status_code == 200
            assert len(result['artifacts']) == 100
            assert result['offset'] is not None

            # Verify offset is properly encoded
            decoded_offset = json.loads(
                base64.b64decode(result['offset']).decode('utf-8')
            )
            assert decoded_offset == next_key

    def test_lambda_handler_multiple_queries_dedup(self):
        """Test lambda_handler with multiple queries and deduplication"""
        from app.jobs.artifacts_list import lambda_handler

        # Mock that returns same artifact for different queries
        duplicate_artifact = Mock(
            name="shared-artifact", id="123", artifact_type="model"
        )

        from app.models.Artifact_Model import Artifact_Model
        with patch.object(Artifact_Model, 'scan_artifacts') as mock_scan:
            mock_scan.side_effect = [
                {'items': [duplicate_artifact], 'last_evaluated_key': None},
                {'items': [duplicate_artifact], 'last_evaluated_key': None}
            ]

            event = {
                'artifact_queries': [
                    {'name': 'shared-artifact'},
                    {'name': '*', 'types': ['model']}
                ],
                'offset': None,
                'auth_token': 'test-token'
            }

            result, status_code = lambda_handler(event, None)

            # Should deduplicate by ID
            assert status_code == 200
            assert len(result['artifacts']) == 1
            assert mock_scan.call_count == 2
