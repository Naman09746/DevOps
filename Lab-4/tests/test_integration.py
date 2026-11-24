"""
Integration Tests - Validating end-to-end chaos engineering fault injection, simulated latency, and probe degradation.
"""
import json
import time

def test_chaos_toggle_unhealthy(client):
    # Set healthy to false
    res = client.post("/api/v1/chaos/toggle", json={"healthy": False})
    assert res.status_code == 200
    assert res.get_json()["current_state"]["healthy"] is False

    # Liveness probe must fail with 503
    probe = client.get("/health")
    assert probe.status_code == 503
    assert probe.get_json()["status"] == "UNHEALTHY"

    # Restore health
    res_restore = client.post("/api/v1/chaos/toggle", json={"healthy": True})
    assert res_restore.status_code == 200
    assert client.get("/health").status_code == 200

def test_chaos_toggle_unready(client):
    # Set readiness to false
    res = client.post("/api/v1/chaos/toggle", json={"ready": False})
    assert res.status_code == 200
    assert res.get_json()["current_state"]["ready"] is False

    # Readiness probe must return 503
    probe = client.get("/ready")
    assert probe.status_code == 503
    assert probe.get_json()["status"] == "NOT_READY"

    # Restore readiness
    client.post("/api/v1/chaos/toggle", json={"ready": True})
    assert client.get("/ready").status_code == 200

def test_traffic_burst_simulation(client):
    for i in range(15):
        resp = client.get("/")
        assert resp.status_code == 200
    
    metrics = client.get("/metrics")
    assert b"http_requests_total" in metrics.data
