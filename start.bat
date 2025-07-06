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
call .venv\Scripts\activate.bat

REM === Always install requirements ===
echo Installing/updating Python packages...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✅ Setup complete!
echo.

REM === Open browser tab (optional) ===
start "" http://localhost:8501

REM === Launch Streamlit ===
python -m streamlit run test_ui.py --server.headless=true --browser.serverAddress=localhost

REM === Optional: just pause before closing ===
echo.
pause
ENDLOCAL
