@echo off
echo ========================================
echo Oxford Examination System
echo ========================================
echo.

cd /d "%~dp0"
backend\venv\Scripts\python.exe start_app.py

pause
