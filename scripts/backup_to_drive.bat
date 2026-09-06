@echo off
setlocal
echo ============================================================
echo  VeggieVerse - Database Backup, Encryption ^& Google Drive Sync
echo ============================================================

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..
cd /d "%REPO_ROOT%"

if not exist ".env" (
    echo [ERROR] .env file not found.
    echo Run scripts\generate_env.bat or copy .env.example to .env first.
    exit /b 1
)

python scripts\backup_to_drive.py %*
if errorlevel 1 (
    echo [ERROR] Backup process encountered an error.
    exit /b 1
)

echo [DONE] Backup completed successfully.
endlocal
