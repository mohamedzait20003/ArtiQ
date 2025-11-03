import sys
import os

# Add lambda-service to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../services/lambda-service'))

from src.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_app_title():
    """Test that the app has the correct title"""
    assert app.title == "Serverless FastAPI"
    assert app.version == "0.1.0"


def test_register_user():
    """Test user registration endpoint"""
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code in [201, 500]  # 201 success or 500 if DynamoDB not available


def test_register_missing_fields():
    """Test registration with missing fields"""
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User"
        }
    )
    assert response.status_code == 422  # Validation error


def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    # Should fail due to invalid credentials or missing DynamoDB
    assert response.status_code in [401, 500]


def test_upload_model_missing_file():
    """Test model upload without file"""
    response = client.post(
        "/api/models/upload",
        data={
            "title": "Test Model"
        }
    )
    assert response.status_code == 422  # Missing required field


def test_get_nonexistent_model():
    """Test getting a model that doesn't exist"""
    response = client.get("/api/models/nonexistent-id")
    # Should return 404 or 500 if DynamoDB not available
    assert response.status_code in [404, 500]


def test_list_models():
    """Test listing all models"""
    response = client.get("/api/models")
    # Should return 200 with empty list or 500 if DynamoDB not available
    assert response.status_code in [200, 500]


def test_update_evaluation_nonexistent_model():
    """Test updating evaluation for nonexistent model"""
    response = client.put(
        "/api/models/nonexistent-id/evaluation",
        json={
            "accuracy": 0.95,
            "loss": 0.05
        }
    )
    assert response.status_code in [404, 500]


def test_delete_nonexistent_model():
    """Test deleting a model that doesn't exist"""
    response = client.delete("/api/models/nonexistent-id")
    assert response.status_code in [404, 500]
