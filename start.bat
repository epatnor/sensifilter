@echo off
SETLOCAL
cd /d %~dp0

REM === Pull latest from Git ===
IF EXIST .git (
    echo 🔄 Pulling latest changes from GitHub...
    git checkout main >nul 2>&1
    git pull
)

REM === Create venv if needed ===
IF NOT EXIST .venv (
    echo 🔧 Creating virtual environment...
    python -m venv .venv
)

REM === Install requirements if needed ===
.\.venv\Scripts\python.exe -m pip show fastapi >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo 📦 Installing requirements...
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\pip.exe install -r requirements.txt
)

REM === Start FastAPI app ===
echo.
echo ✅ Environment ready. Launching Sensifilter web UI...
.\.venv\Scripts\uvicorn.exe main:app --reload --host 127.0.0.1 --port 8000

echo.
echo Server closed. Press any key to exit.
pause
ENDLOCAL
