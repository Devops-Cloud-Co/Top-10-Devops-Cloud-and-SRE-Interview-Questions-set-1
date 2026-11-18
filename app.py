from flask import Flask, jsonify, request
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)
import time
import os
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["endpoint"]
)

APP_VERSION = os.getenv("APP_VERSION", "v1.0")

@app.before_request
def start_timer():
    request.start_time = time.time()


@app.after_request
def record_metrics(response):
    duration = time.time() - request.start_time

    REQUEST_COUNT.labels(
        request.method,
        request.path,
        response.status_code
    ).inc()

    REQUEST_LATENCY.labels(
        request.path
    ).observe(duration)

    return response


@app.route("/")
def home():
    return jsonify({
        "application": "DevOps Demo Application",
        "status": "Running",
        "version": APP_VERSION,
        "message": "Welcome to DevOps troubleshooting lab"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "UP",
        "application": "devops-demo-app",
        "version": APP_VERSION
    }), 200


@app.route("/ready")
def ready():
    return jsonify({
        "status": "READY"
    }), 200


@app.route("/version")
def version():
    return jsonify({
        "version": APP_VERSION
    })


@app.route("/demo/slow")
def slow():
    seconds = request.args.get("seconds", default=3, type=int)
    seconds = max(0, min(seconds, 10))

    time.sleep(seconds)

    return jsonify({
        "message": "Slow API completed",
        "delay_seconds": seconds
    })


@app.route("/demo/error")
def error():
    app.logger.error("Demo application error triggered")

    return jsonify({
        "status": "ERROR",
        "message": "Simulated application failure"
    }), 500


@app.route("/demo/fail")
def fail():
    return jsonify({
        "status": "FAILURE",
        "message": "Simulated failure for troubleshooting"
    }), 503


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {
        "Content-Type": CONTENT_TYPE_LATEST
    }


@app.route("/info")
def info():
    return jsonify({
        "hostname": os.getenv("HOSTNAME", "local"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": APP_VERSION
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8081,
        threaded=True
    )

