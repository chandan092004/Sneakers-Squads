@echo off
title SNEAKER SQUAD - Development Server
echo ========================================================
echo         STARTING SNEAKER SQUAD SERVER
echo ========================================================
echo.

cd /d "%~dp0"

REM 1. Prefer venv python if available
set "PYTHON_EXE="
if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
)

REM 2. If venv python not found, check system python
if "%PYTHON_EXE%"=="" (
    where python >nul 2>&1
    if %errorlevel% equ 0 set "PYTHON_EXE=python"
)

REM 3. If python not found, check Windows launcher 'py'
if "%PYTHON_EXE%"=="" (
    where py >nul 2>&1
    if %errorlevel% equ 0 set "PYTHON_EXE=py"
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python not found on your system!
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Detect local Wi-Fi / LAN IP address for mobile phone access
set LOCAL_IP=127.0.0.1
for /f "tokens=2 delims=:" %%a in ('ipconfig 2^>nul ^| findstr /r /c:"IPv4 Address.*[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*" /c:"IPv4.*[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*"') do (
    for /f "tokens=1" %%b in ("%%a") do (
        set LOCAL_IP=%%b
    )
)

echo ========================================================
echo   Laptop / PC URL:   http://127.0.0.1:8000/
echo   Mobile Phone URL:  http://%LOCAL_IP%:8000/
echo   Admin Portal URL:  http://127.0.0.1:8000/admin/
echo   Admin Username:    admin
echo   Admin Password:    admin123
echo   Database:          PostgreSQL / SQLite (.env supported)
echo ========================================================
echo.
echo Starting Django Server on 0.0.0.0:8000 (Accessible from Phone and PC)...
echo Press Ctrl+C to stop the server.
echo.

"%PYTHON_EXE%" manage.py runserver 0.0.0.0:8000

if %errorlevel% neq 0 (
    echo.
    echo [NOTE] Server stopped with status code %errorlevel%.
)

pause
