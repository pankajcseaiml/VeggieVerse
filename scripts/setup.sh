#!/usr/bin/env bash
# ============================================================
# VeggieVerse Setup Script (Linux/macOS)
# ============================================================
# Run this once on a new machine after cloning the repository.
# Usage: bash scripts/setup.sh
# ============================================================

set -e

echo ""
echo "============================================================"
echo " VeggieVerse / Green Bites - Setup"
echo "============================================================"
echo ""

# ── Check Python ─────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 is not installed."
    echo "Install Python 3.10+ from https://www.python.org/"
    exit 1
fi
echo "[OK] Python found: "

# ── Create virtual environment ───────────────────────────────
if [ ! -d "venv" ]; then
    echo ""
    echo "[STEP] Creating virtual environment..."
    python3 -m venv venv
    echo "[OK] Virtual environment created."
else
    echo "[OK] Virtual environment already exists."
fi

# ── Activate and install dependencies ────────────────────────
echo ""
echo "[STEP] Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt
echo "[OK] Dependencies installed."

# ── Download NLTK data ───────────────────────────────────────
echo ""
echo "[STEP] Downloading NLTK data..."
python3 -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('punkt_tab', quiet=True); print('[OK] NLTK data ready.')"

# ── Set up .env ──────────────────────────────────────────────
echo ""
if [ ! -f ".env" ]; then
    echo "[STEP] Creating .env from .env.example..."
    cp .env.example .env
    echo "[ACTION REQUIRED] Open .env and fill in your secret values:"
    echo ""
    echo "  FLASK_SECRET_KEY  - Generate with: python3 -c 'import secrets; print(secrets.token_hex(32))'"
    echo "  MYSQL_PASSWORD    - Your MySQL root password"
    echo ""
    echo "After filling in .env, run: bash scripts/start.sh"
else
    echo "[OK] .env file already exists."
fi

echo ""
echo "============================================================"
echo " Setup complete! Next steps:"
echo "  1. Edit .env with your actual values (if not done)"
echo "  2. Run MySQL and create the database:"
echo "     mysql -u root -p < database/schema.sql"
echo "  3. Train the model (if model files are missing):"
echo "     bash scripts/train_model.sh"
echo "  4. Start the application:"
echo "     bash scripts/start.sh"
echo "============================================================"
echo ""
