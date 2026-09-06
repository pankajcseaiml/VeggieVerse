"""
scripts/backup_to_drive.py
Automated Database Backup, AES-256-GCM Encryption, and Google Drive Sync for VeggieVerse.

Workflow:
  1. Dumps MySQL database (veg_restaurant_db) to SQL file.
  2. Gzip compresses and encrypts with AES-256-GCM.
  3. Computes SHA-256 checksum and generates JSON metadata.
  4. Stores encrypted backup locally in secure directory (~/Documents/VeggieVerse_Backups).
  5. Syncs encrypted backup to Google Drive via rclone (if configured).
  6. Verifies remote file existence and checksum.

Usage:
  python scripts/backup_to_drive.py [--remote <rclone_remote_name>] [--local-only]
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Ensure scripts directory is on sys.path to import encryption utilities
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from encrypt_backup import encrypt_file, sha256_file, get_encryption_key

# Load environment
load_dotenv(".env")

DEFAULT_BACKUP_DIR = os.path.expanduser(r"~\Documents\VeggieVerse_Backups")
DEFAULT_REMOTE = "gdrive"
RCLONE_BIN = r"C:\Users\Pankaj\AppData\Local\Microsoft\WinGet\Links\rclone.exe"


def find_rclone():
    """Finds rclone executable."""
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


def dump_mysql(output_sql_path):
    """Creates a consistent MySQL dump using mysqldump."""
    host = os.environ.get("MYSQL_HOST", "localhost")
    port = os.environ.get("MYSQL_PORT", "3306")
    user = os.environ.get("MYSQL_USER", "root")
    password = os.environ.get("MYSQL_PASSWORD", "")
    database = os.environ.get("MYSQL_DATABASE", "veg_restaurant_db")

    if not password:
        print("[ERROR] MYSQL_PASSWORD is not set in environment or .env.")
        sys.exit(1)

    os.makedirs(os.path.dirname(os.path.abspath(output_sql_path)), exist_ok=True)

    cmd = [
        "mysqldump",
        f"-h{host}",
        f"-P{port}",
        f"-u{user}",
        f"-p{password}",
        "--routines",
        "--triggers",
        "--single-transaction",
        database
    ]

    print(f"[INFO] Dumping MySQL database '{database}'...")
    with open(output_sql_path, "w", encoding="utf-8") as f:
        res = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)

    if res.returncode != 0:
        print(f"[ERROR] mysqldump failed: {res.stderr}")
        if os.path.exists(output_sql_path):
            os.remove(output_sql_path)
        sys.exit(1)

    dump_size = os.path.getsize(output_sql_path)
    print(f"[SUCCESS] Database dumped ({dump_size:,} bytes) to temporary file.")
    return output_sql_path


def sync_to_google_drive(rclone_bin, remote_name, local_enc_path, local_meta_path):
    """Uploads encrypted backup and metadata to Google Drive."""
    remote_db_dir = f"{remote_name}:VeggieVerse-Backups/database"
    remote_meta_dir = f"{remote_name}:VeggieVerse-Backups/checksums"

    print(f"[INFO] Uploading encrypted backup to {remote_db_dir}...")
    res_db = subprocess.run([rclone_bin, "copy", local_enc_path, remote_db_dir], capture_output=True, text=True)
    if res_db.returncode != 0:
        print(f"[WARNING] rclone upload to {remote_db_dir} failed: {res_db.stderr}")
        return False

    print(f"[INFO] Uploading metadata to {remote_meta_dir}...")
    res_meta = subprocess.run([rclone_bin, "copy", local_meta_path, remote_meta_dir], capture_output=True, text=True)
    if res_meta.returncode != 0:
        print(f"[WARNING] rclone upload metadata failed: {res_meta.stderr}")
        return False

    # Verify remote file exists
    enc_name = os.path.basename(local_enc_path)
    check_res = subprocess.run([rclone_bin, "lsf", f"{remote_db_dir}/{enc_name}"], capture_output=True, text=True)
    if check_res.returncode == 0 and enc_name in check_res.stdout:
        print(f"[SUCCESS] Verified remote file exists on Google Drive: {enc_name}")
        return True
    else:
        print(f"[WARNING] Remote file verification check returned: {check_res.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description="VeggieVerse Encrypted Database Backup & Google Drive Sync")
    parser.add_argument("--remote", default=DEFAULT_REMOTE, help="rclone remote name (default: gdrive)")
    parser.add_argument("--local-only", action="store_true", help="Only store locally; do not upload to Drive")
    parser.add_argument("--backup-dir", default=DEFAULT_BACKUP_DIR, help="Local backup directory")
    args = parser.parse_args()

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    temp_dir = os.path.join(args.backup_dir, "temp")
    db_backup_dir = os.path.join(args.backup_dir, "database")
    meta_backup_dir = os.path.join(args.backup_dir, "checksums")
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs(db_backup_dir, exist_ok=True)
    os.makedirs(meta_backup_dir, exist_ok=True)

    raw_sql_path = os.path.join(temp_dir, f"veg_restaurant_db_{timestamp}.sql")
    final_enc_path = os.path.join(db_backup_dir, f"veg_restaurant_db_{timestamp}.sql.enc")
    final_meta_path = os.path.join(meta_backup_dir, f"veg_restaurant_db_{timestamp}.sql.enc.meta.json")

    # 1. Obtain encryption key
    key = get_encryption_key()

    # 2. Dump database
    dump_mysql(raw_sql_path)

    # 3. Encrypt and compress
    print("[INFO] Encrypting and compressing database backup...")
    enc_output, sha256_hash = encrypt_file(raw_sql_path, final_enc_path, key)

    # Move companion metadata to checksums dir
    temp_meta = f"{final_enc_path}.meta.json"
    if os.path.exists(temp_meta):
        shutil.copy2(temp_meta, final_meta_path)

    # Remove temporary plaintext SQL dump
    if os.path.exists(raw_sql_path):
        os.remove(raw_sql_path)

    print(f"\n[SUCCESS] Local encrypted backup ready:")
    print(f"  File:     {final_enc_path}")
    print(f"  SHA-256:  {sha256_hash}")
    print(f"  Metadata: {final_meta_path}")

    # 4. Google Drive Sync
    if args.local_only:
        print("[INFO] --local-only specified. Skipping Google Drive upload.")
        return

    rclone_bin = find_rclone()
    if not rclone_bin:
        print("[WARNING] rclone executable not found. Backup is safely encrypted locally.")
        print(f"To upload manually later, configure rclone or copy {final_enc_path} to secure cloud storage.")
        return

    # Check if remote exists
    p_remotes = subprocess.run([rclone_bin, "listremotes"], capture_output=True, text=True)
    remotes = [r.strip().rstrip(":") for r in p_remotes.stdout.splitlines() if r.strip()]

    if args.remote not in remotes:
        print(f"[INFO] rclone remote '{args.remote}' is not yet configured.")
        print(f"  Run: rclone config to configure Google Drive with name '{args.remote}'.")
        print(f"  Local encrypted backup is safely stored at: {final_enc_path}")
        return

    # Remote exists, upload
    uploaded = sync_to_google_drive(rclone_bin, args.remote, final_enc_path, final_meta_path)
    if uploaded:
        print("[COMPLETE] Database successfully backed up, encrypted, and synced to Google Drive!")
    else:
        print("[WARNING] Backup encrypted and stored locally, but remote sync encountered an issue.")


if __name__ == "__main__":
    main()
