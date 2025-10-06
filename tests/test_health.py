"""Tests for the FastAPI application root endpoints."""


def test_health_check(client):
    """Tests the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
