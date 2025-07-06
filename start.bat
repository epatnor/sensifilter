@echo off
SETLOCAL
cd /d %~dp0

REM === Skapa venv om den inte finns ===
IF NOT EXIST .venv (
    echo 🔧 Creating virtual environment...
    python -m venv .venv
)

REM === Installera beroenden om streamlit saknas ===
.\.venv\Scripts\python.exe -m pip show streamlit >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo 📦 Installing requirements...
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\pip.exe install -r requirements.txt
)

REM === Starta Streamlit-UI ===
echo.
echo ✅ Environment ready. Starting Sensifilter UI...
start "" http://localhost:8501
.\.venv\Scripts\python.exe -m streamlit run test_ui.py --server.headless true --browser.serverAddress localhost

echo.
echo Streamlit UI closed. Press any key to exit.
pause
ENDLOCAL
