@echo off
REM ============================================================
REM VeggieVerse Verification Script (Windows)
REM ============================================================
REM Checks that the environment is correctly configured.
REM Usage: scripts\verify.bat
REM ============================================================

setlocal enabledelayedexpansion
set PASS=0
set FAIL=0

echo.
echo ============================================================
echo  VeggieVerse Environment Verification
echo ============================================================
echo.

REM ?? Python ???????????????????????????????????????????????????
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [PASS] Python found
    set /a PASS+=1
) else (
    echo [FAIL] Python not found
    set /a FAIL+=1
)

REM ?? Virtual environment ??????????????????????????????????????
if exist "venv\Scripts\python.exe" (
    echo [PASS] Virtual environment found
    set /a PASS+=1
) else (
    echo [FAIL] Virtual environment not found - run scripts\setup.bat
    set /a FAIL+=1
)

REM ?? .env file ????????????????????????????????????????????????
if exist ".env" (
    echo [PASS] .env file found
    set /a PASS+=1
) else (
    echo [FAIL] .env file not found - copy .env.example to .env and fill in values
    set /a FAIL+=1
)

REM ?? Required env vars ????????????????????????????????????????
call venv\Scripts\activate.bat 2>nul
python -c "
import os, sys
from dotenv import load_dotenv
load_dotenv()
required = ['FLASK_SECRET_KEY', 'MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DATABASE']
missing = [v for v in required if not os.environ.get(v)]
if missing:
    print('[FAIL] Missing env vars: ' + ', '.join(missing))
    sys.exit(1)
else:
    print('[PASS] All required environment variables are set')
"
if %ERRORLEVEL% EQU 0 (set /a PASS+=1) else (set /a FAIL+=1)

REM ?? MySQL connectivity ???????????????????????????????????????
python -c "
from dotenv import load_dotenv
load_dotenv()
import os, sys
import mysql.connector
try:
    conn = mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST','localhost'),
        user=os.environ.get('MYSQL_USER','root'),
        password=os.environ.get('MYSQL_PASSWORD',''),
        database=os.environ.get('MYSQL_DATABASE','veg_restaurant_db')
    )
    conn.close()
    print('[PASS] MySQL connection successful')
except Exception as e:
    print(f'[FAIL] MySQL connection failed: {e}')
    sys.exit(1)
"
if %ERRORLEVEL% EQU 0 (set /a PASS+=1) else (set /a FAIL+=1)

REM ?? Model files ??????????????????????????????????????????????
if exist "model\chatbot_model.h5" (
    if exist "model\words.pkl" (
        if exist "model\classes.pkl" (
            echo [PASS] Model files found
            set /a PASS+=1
        ) else (
            echo [FAIL] model\classes.pkl missing - run scripts\train_model.bat
            set /a FAIL+=1
        )
    ) else (
        echo [FAIL] model\words.pkl missing - run scripts\train_model.bat
        set /a FAIL+=1
    )
) else (
    echo [FAIL] model\chatbot_model.h5 missing - run scripts\train_model.bat
    set /a FAIL+=1
)

REM ?? Flask import ?????????????????????????????????????????????
python -c "import flask; print('[PASS] Flask', flask.__version__, 'importable')"
if %ERRORLEVEL% EQU 0 (set /a PASS+=1) else (echo [FAIL] Flask import failed & set /a FAIL+=1)

REM ?? Summary ??????????????????????????????????????????????????
echo.
echo ============================================================
echo  Results: %PASS% passed, %FAIL% failed
if %FAIL% EQU 0 (
    echo  STATUS: ALL CHECKS PASSED - Ready to start!
    echo  Run: scripts\start.bat
) else (
    echo  STATUS: FIX THE FAILURES ABOVE BEFORE STARTING
)
echo ============================================================
echo.
