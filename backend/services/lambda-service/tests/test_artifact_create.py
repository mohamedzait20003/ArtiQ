from unittest.mock import Mock, patch


class TestArtifactCreateLambda:
    """Unit tests for artifact_create lambda function"""

    @patch('app.jobs.artifact_create.invoke_fargate_task')
    @patch('app.jobs.artifact_create.Artifact_Model')
    @patch('app.jobs.artifact_create.uuid.uuid4')
    def test_lambda_handler_success(
        self, mock_uuid, mock_model, mock_invoke_fargate
    ):
        """Test successful artifact creation"""
        from app.jobs.artifact_create import lambda_handler

        # Mock UUID - need to mock str(uuid.uuid4())
        mock_uuid_obj = Mock()
        mock_uuid_obj.__str__ = Mock(return_value="test-id-123")
        mock_uuid.return_value = mock_uuid_obj

        # Mock artifact instance
        mock_artifact = Mock()
        mock_artifact.save.return_value = True
        mock_model.return_value = mock_artifact

        # Mock Fargate task invocation
        mock_invoke_fargate.return_value = {
            'tasks': [{
                'taskArn': 'arn:aws:ecs:us-east-2:123456789012:task/test'
            }]
        }

        event = {
            'artifact_type': 'model',
            'artifact_data': {
                'url': 'https://huggingface.co/bert-base-uncased'
            }
        }

        result, status_code = lambda_handler(event, None)

        assert status_code == 201
        assert 'metadata' in result
        assert 'data' in result
        assert result['metadata']['type'] == 'model'
        # Fixed to match the UUID.hex value
        assert result['metadata']['id'] == 'test-id-123'
        url = 'https://huggingface.co/bert-base-uncased'
        assert result['data']['url'] == url
        
        # Verify Fargate task was invoked for model artifacts
        mock_invoke_fargate.assert_called_once_with('test-id-123')

    @patch('app.jobs.artifact_create.invoke_fargate_task')
    @patch('app.jobs.artifact_create.Artifact_Model')
    @patch('app.jobs.artifact_create.uuid.uuid4')
    def test_lambda_handler_save_failure(
        self, mock_uuid, mock_model, mock_invoke_fargate
    ):
        """Test artifact creation with save failure"""
        from app.jobs.artifact_create import lambda_handler

        # Mock UUID
        mock_uuid_obj = Mock()
        mock_uuid_obj.__str__ = Mock(return_value="test-id-123")
        mock_uuid.return_value = mock_uuid_obj

        # Mock artifact instance to fail save
        mock_artifact = Mock()
        mock_artifact.save.return_value = False
        mock_model.return_value = mock_artifact

        event = {
            'artifact_type': 'model',
            'artifact_data': {
                'url': 'https://huggingface.co/bert-base-uncased'
            }
        }

        result, status_code = lambda_handler(event, None)

        assert status_code == 500
        assert "errorMessage" in result
        assert "Failed to save artifact to database" in result["errorMessage"]
