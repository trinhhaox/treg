# ==============================================================================
# Dockerfile for Treg (Tools Registry) Self-Hosted Runtime
# ==============================================================================
FROM python:3.13-slim

# Install system dependencies (build-essential needed for C-extensions like quickjs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /uvx /bin/

WORKDIR /app

# Copy dependency specifications first for layer caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen --no-install-project

# Copy source code (frontend dashboard is prebuilt in src/treg/web/dashboard)
COPY . .

# Sync final project package
RUN uv sync --frozen

# Environment defaults
ENV PORT=18790 \
    HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1

EXPOSE 18790

# Entrypoint script: run database upgrade then start server
CMD ["sh", "-c", "uv run python -m treg upgrade && uv run python -m treg"]
