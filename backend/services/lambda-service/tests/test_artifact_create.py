import sys
import os
from unittest.mock import Mock, patch

import pytest

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))


class TestArtifactCreateLambda:
    """Unit tests for artifact_create lambda function"""
    
    @patch('app.jobs.artifact_create.Artifact_Model')
    @patch('app.jobs.artifact_create.uuid.uuid4')
    def test_lambda_handler_success(self, mock_uuid, mock_artifact_model):
        """Test successful artifact creation"""
        from app.jobs.artifact_create import lambda_handler
        
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
    
    @patch('app.jobs.artifact_create.Artifact_Model')
    @patch('app.jobs.artifact_create.uuid.uuid4')
    def test_lambda_handler_save_failure(self, mock_uuid, mock_artifact_model):
        """Test artifact creation with save failure"""
        from app.jobs.artifact_create import lambda_handler
        
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
