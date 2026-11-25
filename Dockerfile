# ==============================================================================
# Multi-stage Dockerfile for Treg (Tools Registry) Production Runtime
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Frontend Build (Node.js)
# ------------------------------------------------------------------------------
FROM node:22-alpine AS frontend-builder
WORKDIR /build

# Install dependencies first for layer caching
COPY frontend/package.json frontend/package-lock.json ./frontend/
RUN npm --prefix frontend ci

# Copy web files needed by copy-runtime.mjs & frontend source
COPY src/treg/web/ ./src/treg/web/
COPY frontend/ ./frontend/

# Run type check and Vite production build
RUN npm --prefix frontend run check && npm --prefix frontend run build

# ------------------------------------------------------------------------------
# Stage 2: Production Python Runtime
# ------------------------------------------------------------------------------
FROM python:3.13-slim AS runtime

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for high-speed package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency specifications for layer caching
COPY pyproject.toml uv.lock ./

# Install locked dependencies including [server] extra
RUN uv sync --frozen --no-install-project --no-dev --extra server

# Copy application source code
COPY . .

# Copy prebuilt frontend assets from Stage 1 into web directory
COPY --from=frontend-builder /build/src/treg/web/dashboard ./src/treg/web/dashboard

# Install project package into virtualenv with server extra
RUN uv sync --frozen --no-dev --extra server

# Ensure virtualenv binaries and Python packages are on PATH
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PORT=18790 \
    HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1

EXPOSE 18790

# Healthcheck to verify registry responsiveness
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1:${PORT}/meta || exit 1

# Entrypoint: run DB migrations directly then launch production server instantly
CMD ["sh", "-c", "python -m treg upgrade && python -m treg"]
