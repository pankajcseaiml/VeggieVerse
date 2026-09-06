#!/usr/bin/env bash
# Train the NLP Chatbot Model (Linux/macOS)
set -e
echo ""
echo "[TRAIN] Downloading NLTK data..."
source venv/bin/activate
python3 -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('punkt_tab', quiet=True)"
echo ""
echo "[TRAIN] Training chatbot model (this may take a few minutes)..."
python3 train.py
echo ""
echo "[OK] Model training complete. Files saved to model/"
