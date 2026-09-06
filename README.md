# VeggieVerse — Green Bites 🌿 Restaurant Chatbot

An AI-driven chatbot for a vegetarian restaurant, built with **Flask**, **TensorFlow/Keras**, **NLTK**, and **MySQL**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-green)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.21-orange)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Features

- **NLP Intent Classification** — Custom neural network trained with Keras
- **Multi-turn Conversations** — Step-by-step order placement and table reservation flows
- **Live MySQL Integration** — Menu, orders, reservations, and chat logs stored in MySQL
- **Modern UI** — Responsive, animated, dark-green themed chat interface

---

## Architecture

```
┌────────────────────┐     git clone     ┌──────────────────────┐
│   PRIVATE GITHUB   │ ──────────────►  │   LOCAL MACHINE      │
│                    │                   │                      │
│  Source Code       │                   │  Flask Application   │
│  DB Schema         │                   │  NLP Model           │
│  Scripts           │                   │  venv                │
│  Documentation     │                   └──────┬───────────────┘
│  .env.example      │                          │
└────────────────────┘                          │
                                       ┌────────▼────────────┐
                             ┌─────────┤   MySQL Database     │
                             │         │   veg_restaurant_db  │
              ┌──────────────▼──────┐  └─────────────────────┘
              │  SECURE SECRET      │
              │  STORAGE (.env)     │
              │                     │
              │  FLASK_SECRET_KEY   │
              │  MYSQL_PASSWORD     │
              │  (Password Manager) │
              └─────────────────────┘
```

**Principle:** GitHub holds all code. Secrets never touch GitHub. The `.env` file lives only on your machine and in your password manager.

---

## Requirements

| Dependency | Version |
|---|---|
| Python | 3.10+ (tested on 3.13) |
| MySQL Server | 8.0+ |
| pip | Latest |

---

## Installation on a New Machine

### 1. Clone the Repository

```bash
git clone https://github.com/pankajcseaiml/VeggieVerse.git
cd VeggieVerse/veg_restaurant_chatbot
```

### 2. Run the Setup Script

**Windows:**
```bat
scripts\setup.bat
```

**Linux/macOS:**
```bash
bash scripts/setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies from `requirements.txt`
- Download required NLTK data
- Create a `.env` file from `.env.example` (if it doesn't exist)

### 3. Configure Environment Variables

**Option A (Automated from KeePassXC):**
If your secrets are in KeePassXC, generate `.env` in one command:
```bat
scripts\generate_env.bat
```

**Option B (Manual):**
Open the `.env` file (copied from `.env.example`) and fill in your values:

```bash
# .env  (NEVER commit this file)
FLASK_SECRET_KEY=<generate-below>
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=<your-mysql-password>
MYSQL_DATABASE=veg_restaurant_db
BACKUP_ENCRYPTION_KEY=<generate-below>
```

Generate strong keys:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

> **Security:** Store these values in KeePassXC or your preferred password manager. The `.env` file is git-ignored and must never be committed.


### 4. Set Up the Database

Ensure your MySQL server is running, then:

```bash
# Windows
mysql -u root -p < database\schema.sql

# Linux/macOS
mysql -u root -p < database/schema.sql
```

This creates the `veg_restaurant_db` database with all tables and seeds 10 menu items.

### 5. Train the NLP Model

```bash
# Windows
scripts\train_model.bat

# Linux/macOS
bash scripts/train_model.sh
```

This generates `model/chatbot_model.h5`, `model/words.pkl`, and `model/classes.pkl`.

> **Note:** Model files are included in this repository (they are small — ~250 KB total). Re-training is only needed if you modify `data/intents.json`.

### 6. Verify the Setup

```bash
# Windows
scripts\verify.bat
```

All checks should show `[PASS]`.

### 7. Start the Application

```bash
# Windows
scripts\start.bat

# Linux/macOS
bash scripts/start.sh
```

Open your browser at: **http://localhost:5000**

---

## Environment Variables

All sensitive configuration is loaded from environment variables. Set these in your `.env` file.

| Variable | Required | Description |
|---|---|---|
| `FLASK_SECRET_KEY` | ✅ Yes | Flask session signing key — generate with `secrets.token_hex(32)` |
| `MYSQL_HOST` | ✅ Yes | MySQL server host (e.g. `localhost`) |
| `MYSQL_USER` | ✅ Yes | MySQL username (e.g. `root`) |
| `MYSQL_PASSWORD` | ✅ Yes | MySQL password |
| `MYSQL_DATABASE` | ✅ Yes | Database name (e.g. `veg_restaurant_db`) |
| `MYSQL_PORT` | No | MySQL port (default: `3306`) |
| `FLASK_DEBUG` | No | `1` for debug mode, `0` for production |
| `FLASK_PORT` | No | Port to run Flask on (default: `5000`) |

**If any required variable is missing, the application will exit immediately with a clear error message.**

---

## Database

### Schema

The database has 5 tables:

| Table | Purpose |
|---|---|
| `menu_items` | Restaurant menu (10 items seeded) |
| `orders` | Customer takeaway orders |
| `order_items` | Line items for each order |
| `reservations` | Table reservations |
| `chat_logs` | Full chat history |

Schema is in [`database/schema.sql`](database/schema.sql).

### Backup

```bash
# Windows
scripts\backup_db.bat

# Linux/macOS
bash scripts/backup_db.sh
```

Backups are saved to `backups/veg_restaurant_db_YYYYMMDD_HHMMSS.sql`.

> ⚠️ Store backup files **outside this repository** in secure storage (cloud, encrypted drive).

### Restore

```bash
# Windows — fresh setup from schema
scripts\restore_db.bat

# Windows — restore from a backup
scripts\restore_db.bat backups\veg_restaurant_db_20260906_161500.sql

# Linux/macOS
bash scripts/restore_db.sh backups/veg_restaurant_db_20260906_161500.sql
```

---

## ML Model

The chatbot uses a 3-layer Keras neural network for intent classification.

| File | Purpose |
|---|---|
| `data/intents.json` | Training data — intents, patterns, and responses |
| `train.py` | Model training script |
| `model/chatbot_model.h5` | Trained model weights |
| `model/words.pkl` | Vocabulary |
| `model/classes.pkl` | Intent classes |

Model files are committed because they are small (~250 KB) and reproducible. If they are lost, re-run `scripts/train_model.bat`.

---

## Project Structure

```
veg_restaurant_chatbot/
├── app.py                  # Flask application (main entrypoint)
├── chatbot.py              # NLP inference logic
├── db.py                   # MySQL database layer
├── train.py                # Model training script
├── update_prices.py        # One-off price migration utility
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template (safe to commit)
├── .gitignore              # Git exclusions
├── data/
│   └── intents.json        # NLP training data
├── database/
│   └── schema.sql          # Database schema + seed data
├── model/
│   ├── chatbot_model.h5    # Trained model
│   ├── words.pkl           # Vocabulary
│   └── classes.pkl         # Intent classes
├── static/
│   ├── css/style.css
│   └── js/chat.js
├── templates/
│   └── index.html
├── scripts/
│   ├── setup.bat / setup.sh              # Environment setup & dependency installation
│   ├── start.bat / start.sh              # Application launcher
│   ├── init_keepass.bat                  # KeePassXC database initialization
│   ├── generate_env.bat                  # Auto-generate .env from KeePassXC
│   ├── backup_to_drive.bat / .py         # AES-256-GCM dump & Google Drive upload
│   ├── restore_from_drive.bat / .py      # Google Drive download & database restore
│   ├── verify_backup.bat / .py           # Cryptographic backup verification & audit
│   ├── encrypt_backup.py                 # AES-256-GCM file encryption utility
│   ├── decrypt_backup.py                 # AES-256-GCM file decryption utility
│   ├── train_model.bat / train_model.sh  # NLP model training
│   └── verify.bat                        # Diagnostic environment verification
└── docs/
    ├── DISASTER_RECOVERY.md              # Full disaster recovery procedures
    ├── SECURITY.md                       # Secret separation & encryption specs
    ├── KEEPASSXC_SETUP.md                # KeePassXC secret vault setup guide
    └── GOOGLE_DRIVE_BACKUP.md            # Google Drive rclone sync guide

```

---

## Testing

```bash
# Activate venv first
venv\Scripts\activate    # Windows
source venv/bin/activate # Linux/macOS

# Verify environment
scripts\verify.bat

# Manual test
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "show me the menu"}'
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `[ERROR] FLASK_SECRET_KEY not set` | Copy `.env.example` → `.env` and fill in values |
| `[ERROR] Missing required environment variables` | Check all variables in `.env` are filled |
| `[ERROR] MySQL connection failed` | Check MySQL is running and `MYSQL_PASSWORD` is correct |
| `The chatbot model hasn't been trained yet` | Run `scripts\train_model.bat` |
| `ModuleNotFoundError` | Run `scripts\setup.bat` to install dependencies |
| App won't start | Run `scripts\verify.bat` to diagnose |

---

## Disaster Recovery

If your machine is lost or destroyed, see the complete recovery guide:

📄 **[docs/DISASTER_RECOVERY.md](docs/DISASTER_RECOVERY.md)**

Summary:
1. Get a new machine with Python 3.10+ and MySQL 8.0+
2. `git clone https://github.com/pankajcseaiml/VeggieVerse.git`
3. Retrieve secrets from your password manager
4. `scripts\setup.bat`
5. Restore database from backup
6. `scripts\start.bat`

---

## Security

See [`docs/SECURITY.md`](docs/SECURITY.md) for the full security architecture.

Key principles:
- All secrets in `.env` (git-ignored), never in source code
- `.env.example` contains only placeholder names — safe to commit
- Startup validation: app refuses to start with missing secrets
- Git history has been audited and cleaned

---

## Backup Strategy

| Asset | Where Stored | How to Restore |
|---|---|---|
| Source code | GitHub (private) | `git clone` |
| Secrets | Password manager | Copy to `.env` |
| Database | `backups/` (outside repo) | `scripts\restore_db.bat` |
| Model files | GitHub (small, committed) | Already in repo, or re-run `train.py` |
