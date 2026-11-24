# Multi-Stage Production Dockerfile
# Stage 1: Build & Dependencies
FROM python:3.11-slim AS builder

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Hardened Runtime Container
FROM python:3.11-slim AS runtime

WORKDIR /app

# Create non-privileged system user and group (Least Privilege Security Standard)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/false -m appuser

# Copy installed python dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy application source code
COPY --chown=appuser:appgroup app.py .

# Switch to unprivileged runtime user
USER appuser:appgroup

EXPOSE 8080

# Built-in container health check
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health').read()" || exit 1

ENTRYPOINT ["python3", "app.py"]
