import os
import sys
import pytest

# Ensure app directory is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

from app import app, state

@pytest.fixture
def client():
    app.config["TESTING"] = True
    # Reset state before each test
    state["is_healthy"] = True
    state["is_ready"] = True
    state["chaos_latency_seconds"] = 0.0
    with app.test_client() as client:
        yield client
