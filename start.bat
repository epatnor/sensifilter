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

REM === Launch test UI directly ===
echo Starting Streamlit UI...
start "" http://localhost:8501
python -m streamlit run test_ui.py --server.headless=true --browser.serverAddress=localhost


REM === Deactivate venv after Streamlit ends ===
echo.
call deactivate

pause
ENDLOCAL
