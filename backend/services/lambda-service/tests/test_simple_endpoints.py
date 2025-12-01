from fastapi.testclient import TestClient

from app.main import app


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
