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

REM === Prompt for UI launch
echo Launch test UI?
choice /M "Start test_ui.py now"
IF ERRORLEVEL 2 GOTO end

echo Starting Streamlit UI...
start "" http://localhost:8501
python -m streamlit run test_ui.py

:end
echo.
echo Deactivating venv...
call deactivate

pause
ENDLOCAL
