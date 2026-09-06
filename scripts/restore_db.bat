@echo off
REM ============================================================
REM VeggieVerse Database Restore Script (Windows)
REM ============================================================
REM Usage: scripts\restore_db.bat [backup_file.sql]
REM   If no file given, restores from database\schema.sql (fresh setup)
REM ============================================================

setlocal enabledelayedexpansion

for /f "tokens=1,* delims==" %%a in (.env) do (
    if not "%%a"=="" if not "%%a:~0,1%"=="#" (
        set "%%a=%%b"
    )
)

if "%~1"=="" (
    set RESTORE_FILE=database\schema.sql
    echo [RESTORE] No backup file specified. Using schema.sql for fresh setup.
) else (
    set RESTORE_FILE=%~1
    echo [RESTORE] Restoring from: %RESTORE_FILE%
)

if not exist "%RESTORE_FILE%" (
    echo [ERROR] File not found: %RESTORE_FILE%
    exit /b 1
)

echo [RESTORE] Restoring database %MYSQL_DATABASE%...
mysql -h %MYSQL_HOST% -u %MYSQL_USER% -p%MYSQL_PASSWORD% < "%RESTORE_FILE%"

if %ERRORLEVEL% EQU 0 (
    echo [OK] Database restored successfully.
) else (
    echo [ERROR] Restore failed. Check MySQL credentials in .env
    exit /b 1
)
