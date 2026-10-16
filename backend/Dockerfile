# Multi-stage production Dockerfile for Crop Disease AI Backend
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --user -r /app/requirements.txt

# Final runtime image
FROM python:3.12-slim AS runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Create non-privileged user and upload directory
RUN useradd -m -u 1001 appuser && \
    mkdir -p /app/uploads /app/ml/models /app/ml/reports /app/data && \
    chown -R appuser:appuser /app

# Copy application source code
COPY --chown=appuser:appuser backend/app /app/backend/app
COPY ml/models /app/ml/models
COPY ml/reports /app/ml/reports

# Copy dependencies to appuser home
RUN cp -r /root/.local /home/appuser/.local && \
    chown -R appuser:appuser /home/appuser/.local

USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
