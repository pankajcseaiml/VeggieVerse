@echo off
setlocal
echo ============================================================
echo  VeggieVerse - Database Decryption ^& Restoration from Drive
echo ============================================================

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..
cd /d "%REPO_ROOT%"

if not exist ".env" (
    echo [ERROR] .env file not found.
    echo Run scripts\generate_env.bat or configure .env before restoring.
    exit /b 1
)

python scripts\restore_from_drive.py %*
if errorlevel 1 (
    echo [ERROR] Restoration failed.
    exit /b 1
)

echo [DONE] Restoration complete.
endlocal
