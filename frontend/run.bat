@echo off
echo ========================================
echo AI Study Coach - Frontend
echo ========================================
echo.
echo Starting Streamlit application...
echo Make sure the backend server is running on port 8000
echo.
cd /d "%~dp0"
C:\Users\awaiswaqar\Downloads\kjgh-main\kjgh-main\Study\backend\venv\Scripts\python.exe -m streamlit run app.py
pause
