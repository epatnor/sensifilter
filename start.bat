@echo off
SETLOCAL

REM === Pull latest changes from GitHub ===
echo Pulling latest changes...
git pull origin main

REM === Check if venv exists, else create it ===
IF NOT EXIST .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM === Activate venv ===
call .venv\Scripts\activate

REM === Always install requirements ===
echo Installing/updating Python packages...
pip install --upgrade pip >nul
pip install -r requirements.txt

echo.
echo ✅ Setup complete!
echo.

REM === Launch Streamlit UI in background ===
start "" cmd /c "python -m streamlit run test_ui.py --server.headless=true --browser.serverAddress=localhost"

REM === Wait a moment before opening browser ===
timeout /t 3 >nul
start "" http://localhost:8501

REM === Done ===
pause
ENDLOCAL
