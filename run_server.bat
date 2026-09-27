@echo off
title SNEAKER SQUAD - Development Server
echo ========================================================
echo         STARTING SNEAKER SQUAD SERVER
echo ========================================================
echo.

REM Activate virtual environment if present
if exist "%~dp0venv\Scripts\activate.bat" (
    call "%~dp0venv\Scripts\activate.bat"
)

echo ========================================================
echo   Website URL:       http://127.0.0.1:8000/
echo   Admin Portal URL:  http://127.0.0.1:8000/admin/
echo   Admin Username:    admin
echo   Admin Password:    admin123
echo   Database:          PostgreSQL / SQLite (.env supported)
echo ========================================================
echo.
echo Starting Django Server...
python manage.py runserver 127.0.0.1:8000
pause
