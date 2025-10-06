# pylint: disable=wrong-import-position, redefined-outer-name, unused-argument
"""Configurations for pytest."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.settings import settings


@pytest.fixture
def test_settings(monkeypatch):
    """Fixture to override settings for tests."""
    monkeypatch.setattr(settings, "gemini_api_key", "test_key")
    monkeypatch.setattr(settings, "user_service_url", "http://localhost")
    monkeypatch.setattr(settings, "user_cookie_name", "COWRITE_SESSION_ID")
    monkeypatch.setattr(settings, "database_url", "sqlite+aiosqlite:///:memory:")
    return settings


@pytest.fixture
def client(test_settings):
    """Fixture to create a test client."""
    return TestClient(app)
