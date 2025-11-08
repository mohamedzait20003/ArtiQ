# Standard library imports
import sys
import os
import json
import base64

# Third-party imports
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

# Ensure src is in sys.path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the FastAPI app
from src.main import app

# TestClient instance
client = TestClient(app)



class TestSimpleEndpoints:
    def test_health_endpoint(self):
        """Test /health endpoint returns status ok"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_tracks_endpoint(self):
        """Test /tracks endpoint returns plannedTracks"""
        response = client.get("/tracks")
        assert response.status_code == 200
        data = response.json()
        assert "plannedTracks" in data
        assert isinstance(data["plannedTracks"], list)
        assert "Access control track" in data["plannedTracks"]

class TestArtifactsListLambda:
    """Unit tests for artifacts_list lambda function"""
    
    def test_parse_offset_with_none(self):
        """Test parse_offset with None input"""
        from src.lambda_functions.artifacts_list import parse_offset
        
        result = parse_offset(None)
        assert result is None
    
    def test_parse_offset_with_empty_string(self):
        """Test parse_offset with empty string"""
        from src.lambda_functions.artifacts_list import parse_offset
        
        result = parse_offset("")
        assert result is None
    
    def test_parse_offset_with_valid_base64(self):
        """Test parse_offset with valid base64 encoded JSON"""
        from src.lambda_functions.artifacts_list import parse_offset
        
        # Create valid test data
        test_key = {"id": "test-123", "name": "test-artifact"}
        encoded = base64.b64encode(json.dumps(test_key).encode('utf-8')).decode('utf-8')
        
        result = parse_offset(encoded)
        assert result == test_key
    
    def test_parse_offset_with_invalid_base64(self):
        """Test parse_offset with invalid base64"""
        from src.lambda_functions.artifacts_list import parse_offset
        
        result = parse_offset("invalid-base64!")
        assert result is None
    
    def test_encode_offset_with_none(self):
        """Test encode_offset with None input"""
        from src.lambda_functions.artifacts_list import encode_offset
        
        result = encode_offset(None)
        assert result is None
    
    def test_encode_offset_with_valid_key(self):
        """Test encode_offset with valid DynamoDB key"""
        from src.lambda_functions.artifacts_list import encode_offset
        
        test_key = {"id": "test-123", "name": "test-artifact"}
        result = encode_offset(test_key)
        
        # Verify it's a valid base64 string
        assert isinstance(result, str)
        
        # Verify it can be decoded back
        decoded = base64.b64decode(result.encode('utf-8'))
        decoded_json = json.loads(decoded.decode('utf-8'))
        assert decoded_json == test_key
    
    @patch('src.models.Artifact_Model.Artifact_Model.scan_artifacts')
    def test_lambda_handler_basic_query(self, mock_scan):
        """Test lambda_handler with basic wildcard query"""
        from src.lambda_functions.artifacts_list import lambda_handler
        
        # Mock scan_artifacts response
        mock_artifacts = [
            Mock(name="test-artifact", id="123", artifact_type="model"),
            Mock(name="another-artifact", id="456", artifact_type="dataset")
        ]
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
        
        result = lambda_handler(event, None)
        
        # Verify response structure
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
    
    @patch('src.models.Artifact_Model.Artifact_Model.scan_artifacts')
    def test_lambda_handler_with_name_filter(self, mock_scan):
        """Test lambda_handler with specific name filter"""
        from src.lambda_functions.artifacts_list import lambda_handler
        
        mock_artifacts = [Mock(name="bert-base", id="123", artifact_type="model")]
        mock_scan.return_value = {
            'items': mock_artifacts,
            'last_evaluated_key': None
        }
        
        event = {
            'artifact_queries': [{'name': 'bert-base'}],
            'offset': None,
            'auth_token': 'test-token'
        }
        
        result = lambda_handler(event, None)
        
        assert len(result['artifacts']) == 1
        mock_scan.assert_called_once_with(
            name_filter='bert-base',
            types_filter=None,
            limit=100,
            exclusive_start_key=None
        )
    
    @patch('src.models.Artifact_Model.Artifact_Model.scan_artifacts')
    def test_lambda_handler_with_type_filter(self, mock_scan):
        """Test lambda_handler with type filter"""
        from src.lambda_functions.artifacts_list import lambda_handler
        
        mock_artifacts = [Mock(name="test-model", id="123", artifact_type="model")]
        mock_scan.return_value = {
            'items': mock_artifacts,
            'last_evaluated_key': None
        }
        
        event = {
            'artifact_queries': [{'name': '*', 'types': ['model']}],
            'offset': None,
            'auth_token': 'test-token'
        }
        
        result = lambda_handler(event, None)
        
        assert len(result['artifacts']) == 1
        mock_scan.assert_called_once_with(
            name_filter='*',  # The function passes '*' directly, not None
            types_filter=['model'],
            limit=100,
            exclusive_start_key=None
        )
    
    @patch('src.models.Artifact_Model.Artifact_Model.scan_artifacts')
    def test_lambda_handler_with_pagination(self, mock_scan):
        """Test lambda_handler with pagination"""
        from src.lambda_functions.artifacts_list import lambda_handler
        
        # Mock response with pagination
        mock_artifacts = [Mock(name=f"artifact-{i}", id=str(i), artifact_type="model") for i in range(100)]
        next_key = {"id": "last-item-id"}
        mock_scan.return_value = {
            'items': mock_artifacts,
            'last_evaluated_key': next_key
        }
        
        event = {
            'artifact_queries': [{'name': '*'}],
            'offset': None,
            'auth_token': 'test-token'
        }
        
        result = lambda_handler(event, None)
        
        assert len(result['artifacts']) == 100
        assert result['offset'] is not None
        
        # Verify offset is properly encoded
        decoded_offset = json.loads(base64.b64decode(result['offset']).decode('utf-8'))
        assert decoded_offset == next_key
    
    @patch('src.models.Artifact_Model.Artifact_Model.scan_artifacts')
    def test_lambda_handler_multiple_queries_with_deduplication(self, mock_scan):
        """Test lambda_handler with multiple queries and deduplication"""
        from src.lambda_functions.artifacts_list import lambda_handler
        
        # Mock that returns same artifact for different queries
        duplicate_artifact = Mock(name="shared-artifact", id="123", artifact_type="model")
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
        
        result = lambda_handler(event, None)
        
        # Should deduplicate by ID
        assert len(result['artifacts']) == 1
        assert mock_scan.call_count == 2


class TestRegistryResetLambda:
    """Unit tests for registry_reset lambda function"""
    
    @patch('src.lambda_functions.registry_reset.s3_client')
    @patch('src.lambda_functions.registry_reset.dynamodb')
    def test_lambda_handler_success(self, mock_dynamodb, mock_s3_client):
        """Test successful registry reset"""
        from src.lambda_functions.registry_reset import lambda_handler
        
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
    
    @patch('src.lambda_functions.registry_reset.dynamodb')
    def test_lambda_handler_dynamo_error(self, mock_dynamodb):
        """Test registry reset with DynamoDB error"""
        from src.lambda_functions.registry_reset import lambda_handler
        
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


class TestArtifactCreateLambda:
    """Unit tests for artifact_create lambda function"""
    
    @patch('src.lambda_functions.artifact_create.Artifact_Model')
    @patch('src.lambda_functions.artifact_create.uuid.uuid4')
    def test_lambda_handler_success(self, mock_uuid, mock_artifact_model):
        """Test successful artifact creation"""
        from src.lambda_functions.artifact_create import lambda_handler
        
        # Mock UUID - need to mock str(uuid.uuid4())
        mock_uuid_obj = Mock()
        mock_uuid_obj.__str__ = Mock(return_value="test-id-123")
        mock_uuid.return_value = mock_uuid_obj
        
        # Mock artifact instance
        mock_artifact = Mock()
        mock_artifact.save.return_value = True
        mock_artifact_model.return_value = mock_artifact
        
        event = {
            'artifact_type': 'model',
            'artifact_data': {
                'url': 'https://huggingface.co/bert-base-uncased'
            }
        }
        
        result = lambda_handler(event, None)
        
        assert 'metadata' in result
        assert 'data' in result
        assert result['metadata']['type'] == 'model'
        assert result['metadata']['id'] == 'test-id-123'  # Fixed to match the UUID.hex value
        assert result['data']['url'] == 'https://huggingface.co/bert-base-uncased'
    
    @patch('src.lambda_functions.artifact_create.Artifact_Model')
    @patch('src.lambda_functions.artifact_create.uuid.uuid4')
    def test_lambda_handler_save_failure(self, mock_uuid, mock_artifact_model):
        """Test artifact creation with save failure"""
        from src.lambda_functions.artifact_create import lambda_handler
        
        # Mock UUID
        mock_uuid_obj = Mock()
        mock_uuid_obj.__str__ = Mock(return_value="test-id-123")
        mock_uuid.return_value = mock_uuid_obj
        
        # Mock artifact instance to fail save
        mock_artifact = Mock()
        mock_artifact.save.return_value = False
        mock_artifact_model.return_value = mock_artifact
        
        event = {
            'artifact_type': 'model',
            'artifact_data': {
                'url': 'https://huggingface.co/bert-base-uncased'
            }
        }
        
        with pytest.raises(Exception) as excinfo:
            lambda_handler(event, None)
        
        assert "Failed to save artifact to database" in str(excinfo.value)