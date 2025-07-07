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

REM === Installera beroenden om NiceGUI saknas ===
.\.venv\Scripts\python.exe -m pip show nicegui >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo 📦 Installing requirements...
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\pip.exe install -r requirements.txt
)

REM === Starta NiceGUI-UI ===
echo.
echo ✅ Environment ready. Opening UI in browser...
start "" http://localhost:8080

.\.venv\Scripts\python.exe testnice.py

echo.
echo NiceGUI UI closed. Press any key to exit.
pause
ENDLOCAL
