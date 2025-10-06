"""Tests for the FastAPI application root endpoints."""


def test_health_check(client):
    """Health endpoint should return HTTP 200 and status payload."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
