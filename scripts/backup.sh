#!/usr/bin/env bash
# ==============================================================================
# Treg Database & Configuration Automated Backup Script
# ==============================================================================
set -euo pipefail

BACKUP_DIR="/opt/backups/treg"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
CONTAINER_NAME="treg-app"
LOG_TAG="[treg-backup]"

mkdir -p "$BACKUP_DIR"

echo "$LOG_TAG Starting backup at $(date)"

# 1. Online safe SQLite backup via Python sqlite3.backup (zero locking)
if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
  docker exec "$CONTAINER_NAME" python3 -c '
import sqlite3
src = sqlite3.connect("/app/data/treg.db")
dst = sqlite3.connect("/app/data/backup_temp.db")
src.backup(dst)
dst.close()
src.close()
'
  # Copy out and compress
  docker cp "${CONTAINER_NAME}:/app/data/backup_temp.db" "$BACKUP_DIR/treg_${TIMESTAMP}.sqlite"
  docker exec "$CONTAINER_NAME" rm -f /app/data/backup_temp.db
  gzip -9 "$BACKUP_DIR/treg_${TIMESTAMP}.sqlite"
  echo "$LOG_TAG Database saved to: $BACKUP_DIR/treg_${TIMESTAMP}.sqlite.gz"
else
  echo "$LOG_TAG WARNING: Container $CONTAINER_NAME is not running. Trying direct volume copy."
  VOLUME_PATH=$(docker volume inspect treg_treg-data --format '{{.Mountpoint}}' 2>/dev/null || true)
  if [ -n "$VOLUME_PATH" ] && [ -f "$VOLUME_PATH/treg.db" ]; then
    gzip -c "$VOLUME_PATH/treg.db" > "$BACKUP_DIR/treg_${TIMESTAMP}.sqlite.gz"
    echo "$LOG_TAG Direct volume database saved."
  fi
fi

# 2. Backup configuration (.env)
if [ -f "/opt/treg/.env" ]; then
  tar -czf "$BACKUP_DIR/treg_config_${TIMESTAMP}.tar.gz" -C /opt/treg .env
  echo "$LOG_TAG Config saved to: $BACKUP_DIR/treg_config_${TIMESTAMP}.tar.gz"
fi

# 3. Retention policy: Keep backups for 30 days
DELETED_COUNT=$(find "$BACKUP_DIR" -type f -name "treg_*" -mtime +30 -delete -print 2>/dev/null | wc -l || true)
if [ "$DELETED_COUNT" -gt 0 ]; then
  echo "$LOG_TAG Cleaned up $DELETED_COUNT old backup archives (older than 30 days)."
fi

echo "$LOG_TAG Backup completed successfully at $(date)."
ls -lh "$BACKUP_DIR" | tail -n 5
