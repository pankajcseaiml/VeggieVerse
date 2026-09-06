@echo off
REM ============================================================
REM Train the NLP Chatbot Model (Windows)
REM ============================================================
REM Run this to (re)generate model/chatbot_model.h5, words.pkl, classes.pkl
REM Usage: scripts\train_model.bat
REM ============================================================
echo.
echo [TRAIN] Downloading NLTK data...
call venv\Scripts\activate.bat
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('punkt_tab', quiet=True)"
echo.
echo [TRAIN] Training chatbot model (this may take a few minutes)...
python train.py
echo.
echo [OK] Model training complete. Files saved to model\
