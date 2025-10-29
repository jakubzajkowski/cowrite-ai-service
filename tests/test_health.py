"""Basic health endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_health_ok(client):
    """GET /health should return status OK."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
