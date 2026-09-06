#!/usr/bin/env bash
# ============================================================
# VeggieVerse Database Restore Script (Linux/macOS)
# ============================================================
# Usage: bash scripts/restore_db.sh [backup_file.sql]
# ============================================================
set -e

if [ -f .env ]; then
    export 
fi

RESTORE_FILE=""

if [ ! -f "" ]; then
    echo "[ERROR] File not found: "
    exit 1
fi

echo "[RESTORE] Restoring from: "
mysql -h "" -u "" -p"" < ""
echo "[OK] Database restored successfully."
