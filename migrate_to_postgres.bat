@echo off
title SNEAKER SQUAD - One-Click PostgreSQL Migrator
echo ========================================================
echo       SNEAKER SQUAD - POSTGRESQL MIGRATION TOOL
echo ========================================================
echo.

if exist "%~dp0venv\Scripts\activate.bat" (
    call "%~dp0venv\Scripts\activate.bat"
)

REM Check if DATABASE_URL is already in .env or environment
python -c "import os; from pathlib import Path; p = Path('.env'); exec(open(p).read()) if p.exists() else None; exit(0 if os.environ.get('DATABASE_URL') else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [NOTE] DATABASE_URL nahi mila!
    echo.
    echo Kripya apna PostgreSQL URL yahan paste karein:
    echo (Example: postgresql://postgres:mypassword@localhost:5432/sneaker_db)
    echo (Ya Neon / Supabase / Render ka connection URL)
    echo.
    set /p USER_DB_URL="Enter DATABASE_URL: "
    set DATABASE_URL=%USER_DB_URL%
)

if "%DATABASE_URL%"=="" (
    echo [ERROR] DATABASE_URL provide nahi kiya gaya. Migration cancel ho rahi hai.
    pause
    exit /b 1
)

echo.
echo [1/3] Step 1: Checking connection and applying migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo [ERROR] Migration fail hui. Connection URL check karein.
    pause
    exit /b 1
)

echo.
echo [2/3] Step 2: Loading existing backup data into PostgreSQL...
if exist "%~dp0data_backup.json" (
    python manage.py loaddata "%~dp0data_backup.json"
) else (
    echo [INFO] data_backup.json nahi mila, skipping data load.
)

echo.
echo [3/3] Step 3: Verifying PostgreSQL database...
python manage.py check

echo.
echo ========================================================
echo       SUCCESS! PostgreSQL MIGRATION COMPLETE!
echo ========================================================
echo Ab aap 'run_server.bat' chala kar website use kar sakte hain.
pause
