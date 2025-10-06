# pylint: disable=wrong-import-position, redefined-outer-name, unused-argument
"""Configurations for pytest."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import create_app


@pytest.fixture
def client():
    """Fixture to create a test client."""
    app = create_app()
    return TestClient(app)
