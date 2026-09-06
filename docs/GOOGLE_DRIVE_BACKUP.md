# Google Drive Encrypted Backup & Disaster Recovery Guide

This document details the automated offsite backup pipeline for **VeggieVerse** using **AES-256-GCM encryption** and **rclone**.

---

## 1. Backup Architecture & Security

```text
┌──────────────────────┐
│  MySQL Database      │
│  (veg_restaurant_db) │
└──────────┬───────────┘
           │ 1. mysqldump
           ▼
┌──────────────────────┐
│  Raw SQL Dump        │ (Temporary file in RAM/secure temp directory)
└──────────┬───────────┘
           │ 2. gzip compress (level 9)
           │ 3. AES-256-GCM Encrypt (key from KeePassXC / .env)
           ▼
┌──────────────────────┐
│ Encrypted Archive    │ (.sql.enc)
│ SHA-256 Checksum     │ (.meta.json)
└──────────┬───────────┘
           │ 4. rclone sync (OAuth2 encrypted TLS)
           ▼
┌─────────────────────────────────────────────────────────────┐
│                     GOOGLE DRIVE                            │
│  VeggieVerse-Backups/                                       │
│  ├── database/                                              │
│  │   ├── veg_restaurant_db_20260906_115857.sql.enc          │
│  │   └── ...                                                │
│  ├── checksums/                                             │
│  │   ├── veg_restaurant_db_20260906_115857.sql.enc.meta.json│
│  │   └── checksums.json                                     │
│  └── recovery/                                              │
│      └── RECOVERY_README.txt                                │
└─────────────────────────────────────────────────────────────┘
```

### Critical Security Guarantees:
- **Zero Plaintext Upload**: Plaintext database dumps are NEVER uploaded to Google Drive.
- **Authenticated Encryption**: Uses AES-256-GCM which guarantees both confidentiality and ciphertext integrity (tamper-evident).
- **Separate Key Storage**: The encryption key is stored securely in KeePassXC, NEVER alongside the backups on Google Drive.
- **Multi-Version Retention**: Backups are timestamped and preserved; older backups are never automatically purged without explicit administrative policy.

---

## 2. One-Time Google Drive Setup (rclone)

rclone is pre-installed at `C:\Users\Pankaj\AppData\Local\Microsoft\WinGet\Links\rclone.exe`.

To link your Google Drive:
1. Open PowerShell or Command Prompt.
2. Run:
   ```cmd
   rclone config
   ```
3. Type `n` for **New remote**.
4. Name: `gdrive`
5. Type of storage: Type `drive` (Google Drive)
6. Client ID & Secret: Press `Enter` (leave blank to use defaults)
7. Scope: Type `1` (Full access to files created or opened)
8. Service Account file: Press `Enter` (leave blank)
9. Advanced config: Type `n`
10. Use web browser to automatically authenticate: Type `y`
    - A browser window will open asking you to sign in with Google.
    - Click **Allow** to grant access.
11. Configure as Shared Drive (Team Drive): Type `n`
12. Confirm and save: Type `y`, then `q` to quit.

---

## 3. Creating an Encrypted Backup

To execute the full backup pipeline:
```cmd
scripts\backup_to_drive.bat
```
*(Or Python: `python scripts/backup_to_drive.py`)*

### What happens automatically:
1. Validates presence of `MYSQL_PASSWORD` and `BACKUP_ENCRYPTION_KEY`.
2. Dumps `veg_restaurant_db` via `mysqldump`.
3. Gzip-compresses and encrypts with AES-256-GCM.
4. Generates SHA-256 checksum and metadata JSON.
5. Saves the encrypted artifact to `%USERPROFILE%\Documents\VeggieVerse_Backups\database\`.
6. Securely wipes the plaintext temporary SQL dump.
7. Uploads `.sql.enc` and `.meta.json` to Google Drive `VeggieVerse-Backups/`.
8. Verifies remote file existence.

---

## 4. Verifying Backup Integrity

To audit all local and remote backups:
```cmd
scripts\verify_backup.bat
```
Output report includes:
- File existence & size
- Location (Local vs Remote)
- SHA-256 hash match against JSON metadata
- Decryption authentication test

---

## 5. Restoring Database from Google Drive

To restore the latest backup from Google Drive (or local cache):
```cmd
scripts\restore_from_drive.bat
```

### Advanced Restoration Options:
- **Test in an isolated sandbox database** (does not modify active database):
  ```cmd
  python scripts/restore_from_drive.py --target-db veg_restaurant_db_test
  ```
- **Verify decryption without writing to database**:
  ```cmd
  python scripts/restore_from_drive.py --verify-only
  ```
- **Restore a specific historical backup file**:
  ```cmd
  python scripts/restore_from_drive.py --file veg_restaurant_db_20260906_115857.sql.enc
  ```
