#!/usr/bin/env bash
# ==============================================================================
# Treg 1-Click Production Deployment Script
# Supports: Docker Compose or Native Systemd Service
# ==============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

MODE="${1:-docker}"  # default: docker, or "native"

echo "=================================================="
echo "🚀 Starting Treg Deployment [Mode: ${MODE}]"
echo "Timestamp: $(date -u +"%Y-%m-%d %H:%M:%SZ")"
echo "=================================================="

# 1. Update source code from repository
echo "📥 Pulling latest changes from Git..."
git fetch origin main
CURRENT_COMMIT="$(git rev-parse HEAD)"
LATEST_COMMIT="$(git rev-parse origin/main)"

if [ "$CURRENT_COMMIT" = "$LATEST_COMMIT" ]; then
    echo "ℹ️ Code is already up to date (${CURRENT_COMMIT:0:7}). Continuing deployment checks..."
else
    echo "🔄 Updating from ${CURRENT_COMMIT:0:7} to ${LATEST_COMMIT:0:7}..."
    git pull origin main
fi

# 2. Deployment execution based on chosen mode
if [ "$MODE" = "docker" ]; then
    echo "🐳 Building and deploying with Docker Compose..."
    docker compose build --pull
    docker compose up -d --remove-orphans

    echo "⏳ Waiting for healthcheck to pass..."
    sleep 5
    for i in {1..12}; do
        if curl -sf http://127.0.0.1:18790/meta > /dev/null 2>&1; then
            echo "✅ Treg service is healthy and responding!"
            break
        fi
        echo "   Waiting for service startup (attempt $i/12)..."
        sleep 3
        if [ "$i" -eq 12 ]; then
            echo "❌ Service healthcheck timed out! Printing container logs:"
            docker compose logs --tail=40
            exit 1
        fi
    done

    # Clean up stale builder cache and dangling images
    echo "🧹 Cleaning up unused Docker dangling images..."
    docker image prune -f > /dev/null 2>&1 || true

elif [ "$MODE" = "native" ]; then
    echo "📦 Building Frontend Dashboard..."
    bash scripts/build-dashboard.sh

    echo "🐍 Syncing Python dependencies..."
    if command -v uv > /dev/null 2>&1; then
        uv sync --locked --no-dev
        echo "🗄️ Running database migrations..."
        uv run alembic upgrade head
    else
        echo "❌ 'uv' is not installed. Please install uv first."
        exit 1
    fi

    # Restart systemd service if available
    if command -v systemctl > /dev/null 2>&1 && systemctl is-active --quiet treg; then
        echo "🔄 Restarting Treg systemd service..."
        sudo systemctl restart treg
        sleep 3
        if curl -sf http://127.0.0.1:18790/meta > /dev/null 2>&1; then
            echo "✅ Treg systemd service restarted successfully!"
        else
            echo "❌ Treg service healthcheck failed!"
            sudo journalctl -u treg -n 30 --no-pager
            exit 1
        fi
    else
        echo "ℹ️ Systemd service 'treg' not found or inactive. Native build completed."
    fi
else
    echo "❌ Unknown deployment mode: ${MODE}. Use 'docker' or 'native'."
    exit 1
fi

echo "=================================================="
echo "🎉 Deployment completed successfully!"
echo "=================================================="
