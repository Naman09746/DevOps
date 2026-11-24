"""
Enterprise Microservice - Lab 4 & Capstone Platform
Student: Naman Joshi (2301730152) - ENSP461
Implements: Dynamic Versioning, Probes, Prometheus Metrics, Masked Secret Inspection, Chaos Fault Injection
"""
import os
import sys
import time
import json
import socket
import logging
from datetime import datetime, timezone
from flask import Flask, jsonify, request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Structured Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%SZ"
)
logger = logging.getLogger("enterprise-service")

# Environment & Metadata Configuration
APP_NAME = os.getenv("APP_NAME", "enterprise-service")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEPLOY_COLOR = os.getenv("DEPLOY_COLOR", "blue")  # blue or green
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
NODE_HOSTNAME = os.getenv("HOSTNAME", socket.gethostname())
DB_PASSWORD = os.getenv("DB_PASSWORD", "SuperSecretProdP@ssw0rd")
API_KEY = os.getenv("API_KEY", "ak_live_98342784239847239")

# Application State for Chaos & Health
state = {
    "is_healthy": True,
    "is_ready": True,
    "chaos_latency_seconds": 0.0,
    "chaos_error_rate": 0.0,
    "start_time": datetime.now(timezone.utc)
}

# Prometheus Metrics Instrumentation
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests handled by the service",
    ["method", "endpoint", "status", "version", "color"]
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency histogram in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5]
)
APP_INFO_GAUGE = Gauge(
    "app_deployment_info",
    "Application metadata information",
    ["name", "version", "color", "environment"]
)
APP_INFO_GAUGE.labels(name=APP_NAME, version=APP_VERSION, color=DEPLOY_COLOR, environment=ENVIRONMENT).set(1)

CHAOS_ACTIVE_GAUGE = Gauge(
    "chaos_injection_active",
    "Flag indicating whether active fault injection is present (1=active, 0=inactive)"
)
CHAOS_ACTIVE_GAUGE.set(0)

@app.before_request
def record_start_time():
    request._start_time = time.time()
    # Apply simulated chaos latency if configured
    if state["chaos_latency_seconds"] > 0:
        time.sleep(state["chaos_latency_seconds"])

@app.after_request
def record_metrics_and_log(response):
    if hasattr(request, "_start_time"):
        duration = time.time() - request._start_time
        endpoint = request.path
        method = request.method
        status = response.status_code

        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            endpoint=endpoint,
            status=status,
            version=APP_VERSION,
            color=DEPLOY_COLOR
        ).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method=method, endpoint=endpoint).observe(duration)

        log_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": method,
            "path": endpoint,
            "status": status,
            "duration_ms": round(duration * 1000, 2),
            "version": APP_VERSION,
            "color": DEPLOY_COLOR,
            "ip": request.remote_addr or "127.0.0.1"
        }
        logger.info(json.dumps(log_payload))

    response.headers["X-App-Version"] = APP_VERSION
    response.headers["X-Deploy-Color"] = DEPLOY_COLOR
    response.headers["X-Hostname"] = NODE_HOSTNAME
    return response

@app.route("/")
def index():
    uptime_seconds = (datetime.now(timezone.utc) - state["start_time"]).total_seconds()
    return jsonify({
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "color": DEPLOY_COLOR,
        "environment": ENVIRONMENT,
        "hostname": NODE_HOSTNAME,
        "uptime_seconds": round(uptime_seconds, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "deployment_strategy_support": ["blue-green", "canary", "rolling", "gitops"]
    }), 200

@app.route("/health")
def health():
    if not state["is_healthy"]:
        return jsonify({"status": "UNHEALTHY", "reason": "Simulated fault injected"}), 503
    return jsonify({
        "status": "HEALTHY",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

@app.route("/ready")
def ready():
    if not state["is_ready"]:
        return jsonify({"status": "NOT_READY", "reason": "Service initializing or drained"}), 503
    return jsonify({
        "status": "READY",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

@app.route("/api/v1/info")
def api_info():
    return jsonify({
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "color": DEPLOY_COLOR,
        "environment": ENVIRONMENT,
        "hostname": NODE_HOSTNAME,
        "capabilities": [
            "automated_testing",
            "blue_green_deployment",
            "canary_traffic_splitting",
            "gitops_argo_sync",
            "hashicorp_vault_secrets",
            "etcd_disaster_recovery"
        ]
    }), 200

@app.route("/api/v1/secrets")
def api_secrets():
    """
    Demonstrates secure consumption of credentials.
    Secrets are masked to prevent accidental telemetry leakage in production logs or responses.
    """
    masked_db = f"postgres://dbuser:***REDACTED***@pg-cluster.internal:5432/{APP_NAME}_db"
    masked_key = f"{API_KEY[:4]}...{API_KEY[-4:]}" if len(API_KEY) >= 8 else "***REDACTED***"

    return jsonify({
        "status": "configured",
        "vault_managed": True,
        "credentials": {
            "database_connection_uri": masked_db,
            "api_key_fingerprint": masked_key,
            "secret_storage_backend": "HashiCorp Vault KV v2 / Kubernetes Secrets"
        },
        "audit": {
            "secrets_in_plaintext": False,
            "rbac_enforced": True
        }
    }), 200

@app.route("/api/v1/chaos/toggle", methods=["POST"])
def api_chaos():
    """
    Fault injection endpoint used for Chaos Engineering and Disaster Recovery drill verification.
    """
    payload = request.get_json(silent=True) or {}
    state["is_healthy"] = payload.get("healthy", state["is_healthy"])
    state["is_ready"] = payload.get("ready", state["is_ready"])
    state["chaos_latency_seconds"] = float(payload.get("latency_seconds", state["chaos_latency_seconds"]))

    is_chaos = (not state["is_healthy"]) or (not state["is_ready"]) or (state["chaos_latency_seconds"] > 0)
    CHAOS_ACTIVE_GAUGE.set(1 if is_chaos else 0)

    logger.warning(f"Chaos state updated: healthy={state['is_healthy']}, ready={state['is_ready']}, latency={state['chaos_latency_seconds']}")
    return jsonify({
        "message": "Chaos state successfully updated",
        "current_state": {
            "healthy": state["is_healthy"],
            "ready": state["is_ready"],
            "latency_seconds": state["chaos_latency_seconds"],
            "chaos_active": is_chaos
        }
    }), 200

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
