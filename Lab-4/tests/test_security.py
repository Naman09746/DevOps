"""
DevSecOps & Security Tests - Auditing secret masking, credential leak prevention, and input sanitization.
"""
import json

def test_secret_redaction_in_api(client):
    response = client.get("/api/v1/secrets")
    assert response.status_code == 200
    data = response.get_json()

    # Raw database password or full unmasked token must NEVER appear in output
    raw_text = response.data.decode("utf-8")
    assert "SuperSecretProdP@ssw0rd" not in raw_text
    assert "***REDACTED***" in raw_text
    assert data["audit"]["secrets_in_plaintext"] is False
    assert data["audit"]["rbac_enforced"] is True

def test_invalid_http_method_protection(client):
    # Secrets endpoint should only allow GET
    response = client.delete("/api/v1/secrets")
    assert response.status_code == 405

def test_chaos_bad_payload_handling(client):
    # Non-json or bad payload shouldn't crash the server
    response = client.post("/api/v1/chaos/toggle", data="invalid payload", content_type="text/plain")
    assert response.status_code == 200
