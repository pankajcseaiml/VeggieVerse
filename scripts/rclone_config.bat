@echo off
setlocal
echo ============================================================
echo  VeggieVerse - Configure Google Drive Remote via rclone
echo ============================================================
echo.

set RCLONE_EXE=%LOCALAPPDATA%\Microsoft\WinGet\Links\rclone.exe
if not exist "%RCLONE_EXE%" (
    where rclone >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set RCLONE_EXE=rclone
    ) else (
        echo [ERROR] rclone executable was not found.
        exit /b 1
    )
)

"%RCLONE_EXE%" config
endlocal
