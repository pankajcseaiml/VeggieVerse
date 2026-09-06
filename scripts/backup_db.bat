@echo off
REM ============================================================
REM VeggieVerse Database Backup Script (Windows)
REM ============================================================
REM Reads credentials from .env file.
REM Saves backup to backups\veg_restaurant_db_YYYYMMDD_HHMMSS.sql
REM
REM Usage: scripts\backup_db.bat
REM ============================================================

setlocal enabledelayedexpansion

REM Load .env variables
for /f "tokens=1,* delims==" %%a in (.env) do (
    if not "%%a"=="" if not "%%a:~0,1%"=="#" (
        set "%%a=%%b"
    )
)

REM Create backups directory
if not exist "backups" mkdir backups

REM Generate timestamp
for /f "tokens=2 delims==" %%a in ('wmic OS Get LocalDateTime /value') do set datetime=%%a
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%

set BACKUP_FILE=backups\veg_restaurant_db_%TIMESTAMP%.sql

echo [BACKUP] Creating MySQL backup...
echo [BACKUP] Output: %BACKUP_FILE%
echo.

mysqldump -h %MYSQL_HOST% -u %MYSQL_USER% -p%MYSQL_PASSWORD% --routines --triggers --single-transaction %MYSQL_DATABASE% > "%BACKUP_FILE%" 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [OK] Backup created: %BACKUP_FILE%
    echo.
    echo [IMPORTANT] Store this backup file in a secure location OUTSIDE this repository.
    echo             Recommended: encrypted cloud storage or secure USB drive.
) else (
    echo [ERROR] Backup failed. Check MySQL credentials in .env
    exit /b 1
)
