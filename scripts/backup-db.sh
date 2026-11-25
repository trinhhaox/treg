#!/usr/bin/env bash
# ==============================================================================
# Treg SQLite Database Backup Script with Retention
# Runs locally or inside host cron to backup SQLite DB safely.
# ==============================================================================
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$ROOT_DIR/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP="$(date -u +"%Y%m%d_%H%M%SZ")"

mkdir -p "$BACKUP_DIR"

echo "=================================================="
echo "📦 Starting Treg SQLite Backup"
echo "Timestamp: $TIMESTAMP"
echo "Backup Directory: $BACKUP_DIR"
echo "=================================================="

# Detect SQLite file from volume or path
DB_FILE=""
if [ -f "$ROOT_DIR/treg.db" ]; then
    DB_FILE="$ROOT_DIR/treg.db"
elif [ -f "$ROOT_DIR/treg-dev.db" ]; then
    DB_FILE="$ROOT_DIR/treg-dev.db"
elif [ -f "/var/lib/docker/volumes/treg_treg_data/_data/treg.db" ]; then
    DB_FILE="/var/lib/docker/volumes/treg_treg_data/_data/treg.db"
fi

if [ -n "$DB_FILE" ] && [ -f "$DB_FILE" ]; then
    DEST_FILE="$BACKUP_DIR/treg_${TIMESTAMP}.db.gz"
    echo "Found local DB at $DB_FILE. Creating safe online snapshot..."
    if command -v sqlite3 > /dev/null 2>&1; then
        sqlite3 "$DB_FILE" ".backup '$BACKUP_DIR/treg_temp_${TIMESTAMP}.db'"
        gzip -c "$BACKUP_DIR/treg_temp_${TIMESTAMP}.db" > "$DEST_FILE"
        rm -f "$BACKUP_DIR/treg_temp_${TIMESTAMP}.db"
    else
        gzip -c "$DB_FILE" > "$DEST_FILE"
    fi
    echo "✅ Backup created successfully: $DEST_FILE ($(du -h "$DEST_FILE" | cut -f1))"
elif docker ps --format '{{.Names}}' | grep -q '^treg-app$'; then
    DEST_FILE="$BACKUP_DIR/treg_container_${TIMESTAMP}.db.gz"
    echo "Backing up from running container 'treg-app'..."
    docker exec treg-app python3 -c "
import sqlite3
source = sqlite3.connect('/app/data/treg.db')
dest = sqlite3.connect('/tmp/treg_snapshot.db')
source.backup(dest)
source.close()
dest.close()
"
    docker cp treg-app:/tmp/treg_snapshot.db "$BACKUP_DIR/treg_snapshot.db"
    docker exec treg-app rm -f /tmp/treg_snapshot.db
    gzip -c "$BACKUP_DIR/treg_snapshot.db" > "$DEST_FILE"
    rm -f "$BACKUP_DIR/treg_snapshot.db"
    echo "✅ Container backup created: $DEST_FILE ($(du -h "$DEST_FILE" | cut -f1))"
else
    echo "⚠️ No active database file or container found to back up."
    exit 0
fi

# Retention policy: remove backups older than RETENTION_DAYS
echo "🧹 Pruning backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "treg_*.db.gz" -mtime +"$RETENTION_DAYS" -exec rm -f {} +

echo "🎉 Backup job finished successfully!"
