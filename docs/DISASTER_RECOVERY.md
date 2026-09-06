# Disaster Recovery Guide — VeggieVerse / Green Bites

> **Scenario:** Your laptop is completely lost, destroyed, or wiped.  
> **Goal:** Reconstruct the full working application on a new machine.  
> **Time estimate:** 30–60 minutes depending on internet speed and MySQL setup.

---

## Prerequisites — What You Need

Before you begin, gather these from your **password manager**:

| Item | Where to find it |
|---|---|
| GitHub credentials | Password manager |
| `FLASK_SECRET_KEY` | Password manager |
| `MYSQL_PASSWORD` | Password manager |
| Database backup file | Secure cloud storage or encrypted drive |

---

## Step-by-Step Recovery

### Step 1 — Install System Dependencies

**Python 3.10+**
- Download from: https://www.python.org/downloads/
- Windows: check "Add Python to PATH" during install
- Verify: `python --version`

**MySQL Server 8.0+**
- Download from: https://dev.mysql.com/downloads/mysql/
- Or use XAMPP: https://www.apachefriends.org/
- Verify: `mysql --version`

**Git**
- Download from: https://git-scm.com/
- Verify: `git --version`

---

### Step 2 — Clone the Repository

```bash
git clone https://github.com/pankajcseaiml/VeggieVerse.git
cd VeggieVerse/veg_restaurant_chatbot
```

If prompted, authenticate with your GitHub credentials.

---

### Step 3 — Run Setup

**Windows:**
```bat
scripts\setup.bat
```

**Linux/macOS:**
```bash
bash scripts/setup.sh
```

This creates the virtual environment and installs all dependencies.

---

### Step 4 — Configure Secrets

Open the `.env` file (created by setup script):

```
FLASK_SECRET_KEY=<retrieve from password manager>
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=<retrieve from password manager>
MYSQL_DATABASE=veg_restaurant_db
MYSQL_PORT=3306
FLASK_DEBUG=1
FLASK_PORT=5000
```

Fill in `FLASK_SECRET_KEY` and `MYSQL_PASSWORD` from your password manager.

---

### Step 5 — Restore the Database

**Option A: Restore from backup (recommended — preserves all data)**

```bash
# Windows
scripts\restore_db.bat path\to\veg_restaurant_db_backup.sql

# Linux/macOS
bash scripts/restore_db.sh path/to/veg_restaurant_db_backup.sql
```

**Option B: Fresh setup from schema (loses transactional data, but seeds menu)**

```bash
# Windows
mysql -u root -p < database\schema.sql

# Linux/macOS
mysql -u root -p < database/schema.sql
```

Verify the database:
```sql
mysql -u root -p -e "USE veg_restaurant_db; SHOW TABLES; SELECT COUNT(*) FROM menu_items;"
```

Expected: 5 tables, 10 menu items.

---

### Step 6 — Verify Model Files

The model files (`model/chatbot_model.h5`, `model/words.pkl`, `model/classes.pkl`) are included in the repository.

If they are missing for any reason:
```bash
# Windows
scripts\train_model.bat

# Linux/macOS
bash scripts/train_model.sh
```

---

### Step 7 — Verify the Full Environment

```bash
# Windows
scripts\verify.bat
```

All checks must show `[PASS]`.

---

### Step 8 — Start the Application

```bash
# Windows
scripts\start.bat

# Linux/macOS
bash scripts/start.sh
```

Open: **http://localhost:5000**

---

### Step 9 — Test the Application

Test these scenarios manually:

- [ ] Chat window loads
- [ ] Bot greets on load
- [ ] "Show me the menu" → displays 10 items
- [ ] "Book a table" → starts reservation flow
- [ ] "I want to order" → starts order flow
- [ ] "What are your hours" → responds with hours

---

### Step 10 — First Backup on New Machine

Run a fresh backup immediately:

```bash
scripts\backup_db.bat
```

Store the backup file in your secure cloud storage (outside this repository).

---

## Where Everything Is Stored

| Asset | Storage Location | How to Recover |
|---|---|---|
| All source code | GitHub: `github.com/pankajcseaiml/VeggieVerse` | `git clone` |
| `FLASK_SECRET_KEY` | Password manager | Copy to `.env` |
| `MYSQL_PASSWORD` | Password manager | Copy to `.env` |
| Database backup `.sql` | Secure cloud storage / encrypted drive | Run `scripts\restore_db.bat` |
| ML model files | GitHub (committed — small size) | Already in repo |
| Python dependencies | `requirements.txt` in repo | `pip install -r requirements.txt` |
| DB schema + seed data | `database/schema.sql` in repo | `mysql < database/schema.sql` |

---

## Verification Checklist

After recovery, confirm every item:

```
[ ] Python 3.10+ installed
[ ] MySQL 8.0+ running
[ ] Repository cloned from GitHub
[ ] Virtual environment created
[ ] pip install -r requirements.txt succeeded
[ ] .env file created and filled in
[ ] FLASK_SECRET_KEY set
[ ] MYSQL_PASSWORD set
[ ] veg_restaurant_db database exists
[ ] All 5 tables exist
[ ] 10 menu items in menu_items table
[ ] model/chatbot_model.h5 exists
[ ] model/words.pkl exists
[ ] model/classes.pkl exists
[ ] scripts\verify.bat shows all PASS
[ ] Flask app starts on port 5000
[ ] Chat interface loads in browser
[ ] Menu query returns 10 items
[ ] Order flow works
[ ] Reservation flow works
```

---

## What Is NOT in GitHub (Must Be Retrieved Separately)

| Item | Action |
|---|---|
| Real `.env` file | Retrieve from password manager |
| `FLASK_SECRET_KEY` value | Retrieve from password manager |
| `MYSQL_PASSWORD` value | Retrieve from password manager |
| Database backup (transactional data) | Retrieve from secure backup storage |

---

## Emergency: No Backup Available

If you have no database backup:

1. The **schema + seed data** is fully in `database/schema.sql`
2. Run `mysql -u root -p < database/schema.sql` to restore structure + 10 menu items
3. **Transactional data** (orders, reservations, chat logs) will be lost
4. The application will be **fully functional** — only historical records are gone

This project's architecture means you can always get back to a working state from GitHub + secrets alone.
