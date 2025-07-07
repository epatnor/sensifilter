@echo off
SETLOCAL
cd /d %~dp0

REM === Hämta senaste kod om detta är ett Git-repo ===
IF EXIST .git (
    echo 🔄 Pulling latest changes from GitHub...
    git checkout main >nul 2>&1
    git pull
)

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

REM === Starta Streamlit-UI (i detta terminalfönster) ===
echo.
echo ✅ Environment ready. Opening UI in browser...
start "" http://localhost:8501

REM === Viktigt: runOnSave ger bättre Ctrl+C-respons ===
.\.venv\Scripts\python.exe -m streamlit run test_ui.py --server.headless true --browser.serverAddress localhost --server.runOnSave true

echo.
echo Streamlit UI closed. Press any key to exit.
pause
ENDLOCAL
