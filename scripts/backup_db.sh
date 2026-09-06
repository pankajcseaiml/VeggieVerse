#!/usr/bin/env bash
# ============================================================
# VeggieVerse Database Backup Script (Linux/macOS)
# ============================================================
# Usage: bash scripts/backup_db.sh
# ============================================================
set -e

# Load .env
if [ -f .env ]; then
    export 
fi

mkdir -p backups
TIMESTAMP=
BACKUP_FILE="backups/veg_restaurant_db_.sql"

echo "[BACKUP] Creating MySQL backup..."
echo "[BACKUP] Output: "

mysqldump -h "" -u "" -p"" \
    --routines --triggers --single-transaction \
    "" > ""

echo "[OK] Backup created: "
echo ""
echo "[IMPORTANT] Store this backup file in a secure location OUTSIDE this repository."
echo "            Recommended: encrypted cloud storage or secure USB drive."
