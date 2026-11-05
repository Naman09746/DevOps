import os
import pytest
from app.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json["status"] == "UP"

def test_greeting_endpoint(client):
    res = client.get("/greeting")
    assert res.status_code == 200
    assert "greeting" in res.json

def test_metrics_endpoint(client):
    res = client.get("/metrics")
    assert res.status_code == 200
    assert b"demo_feature_greeting_v2_enabled" in res.data
