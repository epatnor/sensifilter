@echo off
SETLOCAL

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

REM === Optional: prompt for test UI launch ===
set /p launch_ui=Launch test_ui.py? (y/n): 
if /I "%launch_ui%"=="y" (
    python -m streamlit run test_ui.py
)

pause
ENDLOCAL
