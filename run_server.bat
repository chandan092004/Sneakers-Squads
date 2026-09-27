@echo off
title SNEAKER SQUAD - Full Stack Development Server (Django + MySQL)
echo ========================================================
echo   STARTING SNEAKER SQUAD SERVER (Django + MySQL)
echo ========================================================
echo.

REM Check if MySQL is already running on port 3306
netstat -ano | findstr ":3306" | findstr "LISTENING" >nul
if %errorlevel% neq 0 (
    echo [1/2] Starting MySQL Database Server...
    if exist "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe" (
        if not exist "%~dp0mysql_data" (
            mkdir "%~dp0mysql_data"
            "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe" --initialize-insecure --datadir="%~dp0mysql_data" >nul 2>&1
        )
        start /b "" "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqld.exe" --datadir="%~dp0mysql_data" --port=3306 >nul 2>&1
        timeout /t 2 /nobreak >nul
    )
) else (
    echo [1/2] MySQL Database Server is already running!
)

echo [2/2] Starting Django Development Server on http://127.0.0.1:8000 ...
echo.
echo ========================================================
echo   Website URL:       http://127.0.0.1:8000/
echo   Admin Portal URL:  http://127.0.0.1:8000/admin/
echo   Admin Username:    admin
echo   Admin Password:    admin123
echo   Database:          MySQL (sneaker_db)
echo ========================================================
echo.

if exist "%~dp0venv\Scripts\activate.bat" (
    call "%~dp0venv\Scripts\activate.bat"
)
python manage.py runserver 127.0.0.1:8000
pause
