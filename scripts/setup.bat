@echo off
REM ============================================================
REM VeggieVerse Setup Script (Windows)
REM ============================================================
REM Run this once on a new machine after cloning the repository.
REM Usage: scripts\setup.bat
REM ============================================================

echo.
echo ============================================================
echo  VeggieVerse / Green Bites - Setup
echo ============================================================
echo.

REM ?? Check Python ?????????????????????????????????????????????
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Install Python 3.10+ from https://www.python.org/
    exit /b 1
)
echo [OK] Python found:
python --version

REM ?? Create virtual environment ???????????????????????????????
if not exist "venv\" (
    echo.
    echo [STEP] Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created.
) else (
    echo [OK] Virtual environment already exists.
)

REM ?? Activate venv and install dependencies ???????????????????
echo.
echo [STEP] Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip --quiet
pip install -r requirements.txt
echo [OK] Dependencies installed.

REM ?? Download NLTK data ???????????????????????????????????????
echo.
echo [STEP] Downloading NLTK data...
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('punkt_tab', quiet=True); print('[OK] NLTK data ready.')"

REM ?? Set up .env ??????????????????????????????????????????????
echo.
if not exist ".env" (
    echo [STEP] Creating .env from .env.example...
    copy .env.example .env >nul
    echo [ACTION REQUIRED] Open .env and fill in your secret values.
    echo.
    echo   FLASK_SECRET_KEY  - Generate: python -c "import secrets; print(secrets.token_hex(32))"
    echo   MYSQL_PASSWORD    - Your MySQL root password
    echo.
    echo After filling in .env, run: scripts\start.bat
) else (
    echo [OK] .env file already exists.
)

echo.
echo ============================================================
echo  Setup complete! Next steps:
echo   1. Edit .env with your actual values (if not done)
echo   2. Run MySQL and create the database:
echo      mysql -u root -p ^< database\schema.sql
echo   3. Train the model (if model files are missing):
echo      scripts\train_model.bat
echo   4. Start the application:
echo      scripts\start.bat
echo ============================================================
echo.
