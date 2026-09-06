# KeePassXC Secret Storage & Management Guide

This guide documents the enterprise-grade secret management architecture for **VeggieVerse**.

---

## 1. Architecture & Principles

```text
┌─────────────────────────────────────────────────────────────┐
│                 PRIVATE GITHUB REPOSITORY                    │
│ Source Code · Tests · Migrations · Scripts · .env.example   │
│                 (Zero Secrets Permitted)                    │
└──────────────────────────────┬──────────────────────────────┘
                               │ git clone
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      LOCAL MACHINE                          │
│                                                             │
│  ┌────────────────────────┐      ┌───────────────────────┐  │
│  │   KeePassXC Database   │      │      Local .env       │  │
│  │  (Encrypted .kdbx)     ├─────►│  (Git-ignored file)   │  │
│  │  Stored in ~/Documents │      │  Transient dev config │  │
│  └────────────────────────┘      └───────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Security Guarantees:
1. **Zero Secret Exposure**: Secrets are never hardcoded in source code, committed to Git, printed to console, or written to public logs.
2. **KDBX Encryption**: The database is encrypted using industry-standard AES-256 / ChaCha20 with Argon2 key derivation.
3. **External Location**: The `.kdbx` file resides outside the workspace directory (`%USERPROFILE%\Documents\VeggieVerse_Secrets.kdbx`).
4. **Git-Ignored**: Both `.kdbx` and `.env` are strictly excluded in `.gitignore`.

---

## 2. Secret Inventory

The following secrets are managed in KeePassXC under the `/VeggieVerse` entry group:

| Secret Variable | Purpose | Classification | Rotation Recommendation |
|---|---|---|---|
| `FLASK_SECRET_KEY` | Flask session cookie signing key | Critical Secret | Rotate on any suspected leak |
| `MYSQL_HOST` | Database server hostname (`localhost`) | Config | On infrastructure change |
| `MYSQL_PORT` | Database server port (`3306`) | Config | On infrastructure change |
| `MYSQL_USER` | Database user account (`root`) | Config | On user change |
| `MYSQL_PASSWORD` | MySQL root authentication password | Critical Secret | Rotate regularly |
| `MYSQL_DATABASE` | Database name (`veg_restaurant_db`) | Config | On DB rename |
| `BACKUP_ENCRYPTION_KEY` | 256-bit AES-GCM database backup key | Critical Secret | Rotate if backups compromised |

---

## 3. Initial Setup

### Step A: Initialize the Database
Run the interactive setup script in your terminal:
```cmd
scripts\init_keepass.bat
```
*(Or on Linux/macOS: `python scripts/keepass_manager.py init`)*

You will be prompted to enter a **Master Password**:
- Choose a strong, memorable master passphrase.
- The password will **never** be echoed on screen or stored in any script.
- The script automatically imports values from your current `.env` and generates a secure 256-bit `BACKUP_ENCRYPTION_KEY` if not present.

### Step B: Verify the Secret Store
```cmd
python scripts\keepass_manager.py verify
```

---

## 4. Generating the Local `.env` File

Whenever setting up the project on a new machine or after removing `.env`:
```cmd
scripts\generate_env.bat
```
This utility:
1. Prompts for your KeePassXC master password via masked input (`getpass`).
2. Extracts required credentials directly from the encrypted `.kdbx` database.
3. Formats and writes the local `.env` file without echoing values.

---

## 5. Manual KeePassXC GUI Management

You can also inspect and manage secrets using the KeePassXC desktop interface:
1. Launch **KeePassXC**.
2. Open `%USERPROFILE%\Documents\VeggieVerse_Secrets.kdbx`.
3. Unlock with your master password.
4. Navigate to the `VeggieVerse` group to view or update entries.
