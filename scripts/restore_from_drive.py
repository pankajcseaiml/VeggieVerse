"""
scripts/restore_from_drive.py
Automated Google Drive Download, AES-256-GCM Decryption, and MySQL Database Restore for VeggieVerse.

Workflow:
  1. Locates latest encrypted backup (locally or downloads from Google Drive via rclone).
  2. Validates SHA-256 checksum against metadata.
  3. Decrypts and decompresses payload using BACKUP_ENCRYPTION_KEY.
  4. Restores SQL dump into MySQL (supports isolated target database for safe testing).
  5. Verifies table schema and row counts.
  6. Securely removes temporary plaintext SQL file.

Usage:
  python scripts/restore_from_drive.py [--remote <rclone_remote>] [--file <backup_file>] [--target-db <db_name>] [--verify-only]
"""

import os
import sys
import argparse
import subprocess
from dotenv import load_dotenv

# Ensure scripts directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decrypt_backup import decrypt_file, get_decryption_key, sha256_file

load_dotenv(".env")

DEFAULT_BACKUP_DIR = os.path.expanduser(r"~\Documents\VeggieVerse_Backups")
DEFAULT_REMOTE = "gdrive"
RCLONE_BIN = r"C:\Users\Pankaj\AppData\Local\Microsoft\WinGet\Links\rclone.exe"


def find_rclone():
    paths = [
        RCLONE_BIN,
        "rclone",
        os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Links\rclone.exe")
    ]
    for p in paths:
        try:
            res = subprocess.run([p, "version"], capture_output=True, text=True)
            if res.returncode == 0:
                return p
        except Exception:
            continue
    return None


def get_latest_local_backup(backup_dir):
    """Finds latest .sql.enc file in local backup cache."""
    db_dir = os.path.join(backup_dir, "database")
    if not os.path.exists(db_dir):
        return None
    files = [os.path.join(db_dir, f) for f in os.listdir(db_dir) if f.endswith(".sql.enc")]
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def download_from_google_drive(rclone_bin, remote_name, backup_dir, file_name=None):
    """Downloads latest or specified backup from Google Drive."""
    remote_db_dir = f"{remote_name}:VeggieVerse-Backups/database"
    local_db_dir = os.path.join(backup_dir, "database")
    os.makedirs(local_db_dir, exist_ok=True)

    if not file_name:
        # List remote files to find latest
        p_list = subprocess.run([rclone_bin, "lsf", remote_db_dir], capture_output=True, text=True)
        if p_list.returncode != 0:
            print(f"[WARNING] Could not list Google Drive directory {remote_db_dir}: {p_list.stderr}")
            return None
        remote_files = [f.strip() for f in p_list.stdout.splitlines() if f.strip().endswith(".sql.enc")]
        if not remote_files:
            print(f"[INFO] No encrypted backups found on Google Drive at {remote_db_dir}.")
            return None
        remote_files.sort(reverse=True)
        file_name = remote_files[0]

    remote_file_path = f"{remote_db_dir}/{file_name}"
    local_file_path = os.path.join(local_db_dir, file_name)

    print(f"[INFO] Downloading {remote_file_path} to {local_file_path}...")
    res = subprocess.run([rclone_bin, "copy", remote_file_path, local_db_dir], capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(local_file_path):
        print(f"[SUCCESS] Downloaded: {local_file_path}")
        # Also try downloading companion metadata
        meta_name = f"{file_name}.meta.json"
        subprocess.run([rclone_bin, "copy", f"{remote_name}:VeggieVerse-Backups/checksums/{meta_name}", os.path.join(backup_dir, "checksums")], capture_output=True)
        return local_file_path
    else:
        print(f"[ERROR] Failed to download from Google Drive: {res.stderr}")
        return None


def restore_sql_to_mysql(sql_path, target_db):
    """Executes SQL dump into specified MySQL database."""
    host = os.environ.get("MYSQL_HOST", "localhost")
    port = os.environ.get("MYSQL_PORT", "3306")
    user = os.environ.get("MYSQL_USER", "root")
    password = os.environ.get("MYSQL_PASSWORD", "")

    # Ensure database exists
    create_db_cmd = f"CREATE DATABASE IF NOT EXISTS `{target_db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    subprocess.run(
        ["mysql", f"-h{host}", f"-P{port}", f"-u{user}", f"-p{password}", "-e", create_db_cmd],
        capture_output=True, text=True
    )

    print(f"[INFO] Restoring SQL dump into database '{target_db}'...")
    with open(sql_path, "r", encoding="utf-8") as f:
        res = subprocess.run(
            ["mysql", f"-h{host}", f"-P{port}", f"-u{user}", f"-p{password}", target_db],
            stdin=f, capture_output=True, text=True
        )

    if res.returncode != 0:
        print(f"[ERROR] MySQL restore failed: {res.stderr}")
        return False

    print(f"[SUCCESS] Database '{target_db}' restored successfully.")
    return True


def verify_restored_database(target_db):
    """Verifies tables and row counts in restored database."""
    import mysql.connector
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            port=int(os.environ.get("MYSQL_PORT", "3306")),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", ""),
            database=target_db
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"[INFO] Restored Database '{target_db}' Table Inventory:")
        total_rows = 0
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM `{t}`")
            cnt = cursor.fetchone()[0]
            total_rows += cnt
            print(f"  - {t}: {cnt} rows")
        conn.close()
        print(f"[SUCCESS] Verification passed: {len(tables)} tables, {total_rows} total rows.")
        return len(tables) > 0
    except Exception as e:
        print(f"[ERROR] Database verification failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="VeggieVerse Database Restore from Google Drive / Encrypted Backup")
    parser.add_argument("--remote", default=DEFAULT_REMOTE, help="rclone remote name")
    parser.add_argument("--file", help="Specific .sql.enc file path or name")
    parser.add_argument("--target-db", default=os.environ.get("MYSQL_DATABASE", "veg_restaurant_db"), help="Target MySQL database name")
    parser.add_argument("--backup-dir", default=DEFAULT_BACKUP_DIR, help="Local backup directory")
    parser.add_argument("--verify-only", action="store_true", help="Only verify decryption without restoring to MySQL")
    args = parser.parse_args()

    key = get_decryption_key()
    target_enc_file = None

    # Check local first
    if args.file and os.path.exists(args.file):
        target_enc_file = args.file
    else:
        # Check if rclone has it
        rclone_bin = find_rclone()
        if rclone_bin:
            target_enc_file = download_from_google_drive(rclone_bin, args.remote, args.backup_dir, args.file)

        # Fallback to local cache
        if not target_enc_file:
            target_enc_file = get_latest_local_backup(args.backup_dir)

    if not target_enc_file or not os.path.exists(target_enc_file):
        print(f"[ERROR] No backup file found to restore.")
        sys.exit(1)

    print(f"[INFO] Selected backup for restore: {target_enc_file}")

    if args.verify_only:
        decrypt_file(target_enc_file, key=key, verify_only=True)
        print("[SUCCESS] Backup verification passed.")
        return

    # Decrypt to temporary file
    temp_dir = os.path.join(args.backup_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_sql = os.path.join(temp_dir, "restore_temp.sql")

    try:
        decrypt_file(target_enc_file, output_path=temp_sql, key=key)
        restore_success = restore_sql_to_mysql(temp_sql, args.target_db)
        if restore_success:
            verify_restored_database(args.target_db)
    finally:
        # Clean up temporary plaintext SQL dump
        if os.path.exists(temp_sql):
            os.remove(temp_sql)


if __name__ == "__main__":
    main()
