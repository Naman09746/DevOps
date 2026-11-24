"""
Unit Tests - Testing route responses, status codes, headers, and Prometheus metric outputs.
"""
import json

def test_index_route(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "color" in data
    assert "hostname" in data
    assert "deployment_strategy_support" in data
    assert "blue-green" in data["deployment_strategy_support"]

def test_health_liveness_probe(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "HEALTHY"

def test_readiness_probe(client):
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "READY"

def test_api_info_endpoint(client):
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.get_json()
    assert data["app_name"] == "enterprise-service"
    assert "gitops_argo_sync" in data["capabilities"]

def test_custom_response_headers(client):
    response = client.get("/")
    assert "X-App-Version" in response.headers
    assert "X-Deploy-Color" in response.headers
    assert "X-Hostname" in response.headers

def test_metrics_endpoint(client):
    # Trigger a request first to increment counters
    client.get("/")
    response = client.get("/metrics")
    assert response.status_code == 200
    content = response.data.decode("utf-8")
    assert "http_requests_total" in content
    assert "app_deployment_info" in content
