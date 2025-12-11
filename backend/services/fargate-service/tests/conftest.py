"""
Pytest configuration for fargate-service tests

This configuration provides shared setup, mocks, and library configuration
for all tests in the fargate service.
"""
import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock

# Add backend lib and app directories to sys.path
backend_lib = Path(__file__).parent.parent.parent.parent / 'lib'
app_dir = Path(__file__).parent.parent / 'app'
include_dir = Path(__file__).parent.parent

for path in [backend_lib, app_dir, include_dir]:
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


# =============================================================================
# Environment and Configuration Fixtures
# =============================================================================

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock common environment variables for testing"""
    env_vars = {
        'AWS_REGION': 'us-east-1',
        'AWS_ACCESS_KEY_ID': 'test-access-key',
        'AWS_SECRET_ACCESS_KEY': 'test-secret-key',
        'LOG_LEVEL': 'DEBUG',
        'GITHUB_TOKEN': 'test-github-token',
        'HUGGINGFACE_TOKEN': 'test-hf-token',
        'DATABASE_URL': 'sqlite:///:memory:',
    }
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)
    return env_vars


# =============================================================================
# Mock External Service Clients
# =============================================================================

@pytest.fixture
def mock_github_client():
    """Mock GitHub API client"""
    mock = MagicMock()
    mock.get_repository.return_value = {
        'name': 'test-repo',
        'owner': 'test-owner',
        'description': 'Test repository',
        'stars': 1000,
        'forks': 100,
        'open_issues': 10,
        'default_branch': 'main',
        'license': 'MIT',
        'created_at': '2020-01-01T00:00:00Z',
        'updated_at': '2025-12-06T00:00:00Z'
    }
    mock.get_contributors.return_value = [
        {'login': 'user1', 'contributions': 50},
        {'login': 'user2', 'contributions': 30}
    ]
    mock.get_commits.return_value = []
    mock.get_issues.return_value = []
    mock.get_pull_requests.return_value = []
    return mock


@pytest.fixture
def mock_huggingface_client():
    """Mock HuggingFace API client"""
    mock = MagicMock()
    mock.get_model.return_value = {
        'name': 'test-model',
        'author': 'test-author',
        'downloads': 5000,
        'likes': 250,
        'tags': ['nlp', 'transformer']
    }
    return mock


@pytest.fixture
def mock_aws_s3():
    """Mock AWS S3 client"""
    mock = MagicMock()
    mock.upload_file.return_value = True
    mock.download_file.return_value = True
    mock.list_objects.return_value = {'Contents': []}
    return mock


@pytest.fixture
def mock_aws_ecr():
    """Mock AWS ECR client"""
    mock = MagicMock()
    mock.get_authorization_token.return_value = {
        'authorizationData': [{
            'authorizationToken': 'dGVzdDp0ZXN0',
            'proxyEndpoint': 'https://test.ecr.us-east-1.amazonaws.com'
        }]
    }
    return mock


# =============================================================================
# Mock Database Models
# =============================================================================

@pytest.fixture
def mock_artifact_model():
    """Mock Artifact model"""
    mock = MagicMock()
    mock.create.return_value = {
        'id': 'test-artifact-123',
        'name': 'test-package',
        'version': '1.0.0',
        'url': 'https://github.com/example/test-package',
        'created_at': '2025-12-06T00:00:00Z'
    }
    mock.find.return_value = None
    mock.update.return_value = True
    mock.delete.return_value = True
    return mock


@pytest.fixture
def mock_rating_model():
    """Mock Rating model"""
    mock = MagicMock()
    mock.create.return_value = {
        'id': 'test-rating-123',
        'artifact_id': 'test-artifact-123',
        'BusFactor': 0.8,
        'Correctness': 0.9,
        'RampUp': 0.7,
        'ResponsiveMaintainer': 0.85,
        'LicenseScore': 1.0,
        'GoodPinningPractice': 0.6,
        'PullRequest': 0.75,
        'NetScore': 0.82
    }
    return mock


# =============================================================================
# Sample Data Fixtures
# =============================================================================

@pytest.fixture
def sample_github_url():
    """Sample GitHub package URL"""
    return "https://github.com/lodash/lodash"


@pytest.fixture
def sample_npm_url():
    """Sample npm package URL"""
    return "https://www.npmjs.com/package/express"


@pytest.fixture
def sample_artifact_data():
    """Sample artifact data structure"""
    return {
        'id': 'artifact-001',
        'name': 'lodash',
        'version': '4.17.21',
        'url': 'https://github.com/lodash/lodash',
        'metadata': {
            'description': 'A modern JavaScript utility library',
            'license': 'MIT'
        }
    }


@pytest.fixture
def sample_rating_data():
    """Sample rating data structure"""
    return {
        'BusFactor': 0.85,
        'Correctness': 0.92,
        'RampUp': 0.78,
        'ResponsiveMaintainer': 0.88,
        'LicenseScore': 1.0,
        'GoodPinningPractice': 0.65,
        'PullRequest': 0.80,
        'NetScore': 0.84
    }
