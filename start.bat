@echo off
SETLOCAL

REM === Gå till skriptets katalog ===
cd /d %~dp0

REM === Kontrollera om .venv finns, annars skapa ===
IF NOT EXIST .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM === Installera krav om streamlit saknas i venv ===
.\.venv\Scripts\python.exe -m pip show streamlit >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Installing requirements...
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\pip.exe install -r requirements.txt
)

REM === Döda ev. hängande streamlit-processer ===
for /f "tokens=2 delims=," %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq streamlit*" /FO CSV ^| find /I "python.exe"') do (
    taskkill /PID %%a /F >nul 2>&1
)

REM === Kör test_ui.py ===
echo.
echo ✅ Environment ready. Starting Sensifilter UI...
echo.
start "" http://localhost:8501
.\.venv\Scripts\python.exe -m streamlit run test_ui.py --server.headless=true --browser.serverAddress=localhost

echo.
echo Streamlit UI closed. Press any key to exit.
pause
ENDLOCAL
