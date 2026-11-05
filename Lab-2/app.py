import os
import socket
from flask import Flask, jsonify

app = Flask(__name__)
VISITOR_COUNT = 0
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_ENV = os.getenv("APP_ENV", "production")

@app.route("/")
def index():
    global VISITOR_COUNT
    VISITOR_COUNT += 1
    return jsonify({
        "status": "success",
        "message": "Welcome to Cloud-Native Kubernetes & Docker Microservice",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "pod_hostname": socket.gethostname(),
        "visitor_count": VISITOR_COUNT
    })

@app.route("/healthz")
def liveness():
    return jsonify({"status": "healthy"}), 200

@app.route("/ready")
def readiness():
    return jsonify({"status": "ready"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
