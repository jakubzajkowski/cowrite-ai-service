# pylint: disable=wrong-import-position, redefined-outer-name, unused-argument
"""Configurations for pytest."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.settings import Settings


@pytest.fixture
def test_settings():
    """Fixture to override settings for tests."""
    return Settings(
        gemini_api_key="test_key",
        user_service_url="http://localhost",
        user_cookie_name="COWRITE_SESSION_ID",
        database_url="sqlite+aiosqlite:///:memory:",
    )


@pytest.fixture
def client(test_settings):
    """Fixture to create a test client."""
    app = create_app(settings=test_settings)
    return TestClient(app)
