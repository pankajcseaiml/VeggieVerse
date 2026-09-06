@echo off
setlocal
echo ============================================================
echo  VeggieVerse - Generate .env from KeePassXC Secret Store
echo ============================================================

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..
cd /d "%REPO_ROOT%"

python scripts\keepass_manager.py generate-env %*
if errorlevel 1 (
    echo [ERROR] Failed to generate .env from KeePassXC.
    exit /b 1
)

echo [SUCCESS] .env successfully written from KeePassXC.
endlocal
