"""Tests for health router."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health router coverage (line 8)."""

    def should_return_health_status(self):
        """Test line 8: health endpoint returns status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
