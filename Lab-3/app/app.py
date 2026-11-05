import os
import json
import logging
from datetime import datetime, timezone
from flask import Flask, jsonify, request
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Structured Logging Setup
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("demo-app")

# Prometheus Metrics
REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests received",
    ["method", "endpoint", "status"]
)
FEATURE_FLAG_GAUGE = Gauge(
    "demo_feature_greeting_v2_enabled",
    "Current status of greeting v2 feature flag (1=active, 0=inactive)"
)

def is_v2_enabled():
    val = os.getenv("FEATURE_GREETING_V2", "true").lower() in ("true", "1", "yes")
    FEATURE_FLAG_GAUGE.set(1 if val else 0)
    return val

@app.before_request
def log_request_start():
    request._start_time = datetime.now(timezone.utc)

@app.after_request
def log_request_end(response):
    endpoint = request.path
    method = request.method
    status = response.status_code
    REQUESTS_TOTAL.labels(method=method, endpoint=endpoint, status=status).inc()

    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": "INFO",
        "method": method,
        "path": endpoint,
        "status": status,
        "ip": request.remote_addr
    }
    logger.info(json.dumps(log_entry))
    return response

@app.route("/")
def index():
    return jsonify({
        "status": "online",
        "service": "Lab 3 DevSecOps & Observability Microservice",
        "version": "1.0.0"
    })

@app.route("/health")
def health():
    return jsonify({
        "status": "UP",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200

@app.route("/greeting")
def greeting():
    if is_v2_enabled():
        return jsonify({
            "greeting": "Hello, Cloud-Native DevOps Engineer! (V2 Active)",
            "feature_v2": True
        })
    return jsonify({
        "greeting": "Hello, World! (Legacy V1)",
        "feature_v2": False
    })

@app.route("/metrics")
def metrics():
    is_v2_enabled()
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
