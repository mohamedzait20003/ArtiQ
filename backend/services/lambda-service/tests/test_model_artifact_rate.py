"""
Tests for model_artifact_rate endpoint
"""
from unittest.mock import Mock, patch


class TestModelArtifactRate:
    """Unit tests for model_artifact_rate lambda function"""

    @patch('app.jobs.model_artifact_rate.Artifact_Model')
    def test_lambda_handler_success(self, mock_artifact):
        """Test successful rating retrieval"""
        from app.jobs.model_artifact_rate import lambda_handler

        # Mock rating object
        mock_rating = Mock()
        mock_rating.net_score = {'value': 0.85, 'latency': 0.5}
        mock_rating.ramp_up_time = {'value': 0.75, 'latency': 1.2}
        mock_rating.bus_factor = {'value': 0.6, 'latency': 0.8}
        mock_rating.performance_claims = {'value': 0.9, 'latency': 2.1}
        mock_rating.license = {'value': 1.0, 'latency': 0.3}
        mock_rating.dataset_and_code_score = {'value': 0.8, 'latency': 1.5}
        mock_rating.dataset_quality = {'value': 0.7, 'latency': 1.0}
        mock_rating.code_quality = {'value': 0.85, 'latency': 1.8}
        mock_rating.reproducibility = {'value': 0.65, 'latency': 0.4}
        mock_rating.reviewedness = {'value': 0.55, 'latency': 0.6}
        mock_rating.tree_score = {'value': 0.7, 'latency': 0.7}
        mock_rating.size_score = {
            'value': {
                'raspberry_pi': 0.3,
                'jetson_nano': 0.5,
                'desktop_pc': 0.8,
                'aws_server': 1.0
            },
            'latency': 0.2
        }

        # Mock artifact instance
        mock_artifact_instance = Mock()
        mock_artifact_instance.name = 'test-model'
        mock_artifact_instance.artifact_type = 'model'
        mock_artifact_instance.category = 'nlp'
        mock_artifact_instance.rating.return_value = mock_rating
        mock_artifact.get.return_value = mock_artifact_instance

        event = {'artifact_id': 'test-123'}
        result, status_code = lambda_handler(event, None)

        assert status_code == 200
        assert result['name'] == 'test-model'
        # category comes from artifact.category attribute
        assert result['net_score'] == 0.85
        assert result['net_score_latency'] == 0.5
        assert result['size_score']['raspberry_pi'] == 0.3
        assert result['size_score_latency'] == 0.2

    @patch('app.jobs.model_artifact_rate.Artifact_Model')
    def test_lambda_handler_artifact_not_found(self, mock_artifact):
        """Test artifact not found"""
        from app.jobs.model_artifact_rate import lambda_handler

        mock_artifact.get.return_value = None

        event = {'artifact_id': 'nonexistent-123'}
        result, status_code = lambda_handler(event, None)

        assert status_code == 404
        assert 'errorMessage' in result
        assert 'does not exist' in result['errorMessage']

    @patch('app.jobs.model_artifact_rate.Artifact_Model')
    def test_lambda_handler_not_model_artifact(self, mock_artifact):
        """Test non-model artifact"""
        from app.jobs.model_artifact_rate import lambda_handler

        # Mock artifact as dataset
        mock_artifact_instance = Mock()
        mock_artifact_instance.artifact_type = 'dataset'
        mock_artifact.get.return_value = mock_artifact_instance

        event = {'artifact_id': 'dataset-123'}
        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert 'errorMessage' in result
        assert 'not a model artifact' in result['errorMessage']

    @patch('app.jobs.model_artifact_rate.Artifact_Model')
    def test_lambda_handler_rating_not_found(self, mock_artifact):
        """Test rating not found for artifact"""
        from app.jobs.model_artifact_rate import lambda_handler

        # Mock artifact instance without rating
        mock_artifact_instance = Mock()
        mock_artifact_instance.artifact_type = 'model'
        mock_artifact_instance.rating.return_value = None
        mock_artifact.get.return_value = mock_artifact_instance

        event = {'artifact_id': 'test-123'}
        result, status_code = lambda_handler(event, None)

        assert status_code == 404
        assert 'errorMessage' in result
        assert 'No rating found' in result['errorMessage']

    def test_lambda_handler_missing_artifact_id(self):
        """Test missing artifact_id in event"""
        from app.jobs.model_artifact_rate import lambda_handler

        event = {}
        result, status_code = lambda_handler(event, None)

        assert status_code == 400
        assert 'errorMessage' in result
        assert 'artifact_id is required' in result['errorMessage']

    @patch('app.jobs.model_artifact_rate.Artifact_Model')
    def test_lambda_handler_database_error(self, mock_artifact):
        """Test database error during retrieval"""
        from app.jobs.model_artifact_rate import lambda_handler

        # Simulate database error
        mock_artifact.get.side_effect = Exception("Database connection error")

        event = {'artifact_id': 'test-123'}
        result, status_code = lambda_handler(event, None)

        assert status_code == 500
        assert 'errorMessage' in result
        assert 'encountered an error' in result['errorMessage']
