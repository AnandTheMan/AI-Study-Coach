@echo off
echo ========================================
echo AI Study Coach
echo ========================================
echo.

cd /d "%~dp0"
backend\venv\Scripts\python.exe start_app.py

pause
