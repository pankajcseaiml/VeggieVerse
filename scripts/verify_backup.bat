@echo off
setlocal
echo ============================================================
echo  VeggieVerse - Backup Integrity ^& Recovery Audit
echo ============================================================

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..
cd /d "%REPO_ROOT%"

python scripts\verify_backup.py %*
endlocal
