@echo off
setlocal
echo ============================================================
echo  VeggieVerse - Initialize KeePassXC Secret Database
echo ============================================================
echo.
echo This utility creates an encrypted KeePassXC database (.kdbx)
echo located OUTSIDE the repository at:
echo   %USERPROFILE%\Documents\VeggieVerse_Secrets.kdbx
echo.
echo You will be prompted to enter your chosen Master Password.
echo Your password is never stored or echoed on screen.
echo.

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..
cd /d "%REPO_ROOT%"

python scripts\keepass_manager.py init %*
if errorlevel 1 (
    echo.
    echo [ERROR] KeePassXC initialization encountered an error.
    exit /b 1
)

echo.
echo [DONE] KeePassXC secret store is ready.
endlocal
