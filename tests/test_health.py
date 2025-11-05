"""Unit tests for health endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_ok(client):
    """GET /health should return status OK without loading ML models.

    This is a smoke test verifying the application starts correctly
    with mocked dependencies.
    """
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
