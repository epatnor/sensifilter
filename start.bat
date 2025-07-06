@echo off
echo [🔧] Setting up sensifilter environment...

REM Check if venv exists
if not exist ".venv\" (
    echo [📦] Creating virtual environment...
    python -m venv .venv
)

REM Activate venv (Windows)
call .venv\Scripts\activate.bat

REM Upgrade pip
echo [⬆️ ] Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo [📥] Installing dependencies...
pip install -r requirements.txt

REM Run preload script (downloads models etc)
echo [🔽] Downloading models...
python preload_models.py

echo [✅] Setup complete!
pause
