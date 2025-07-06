@echo off
SETLOCAL

REM === Gå till skriptets katalog ===
cd /d %~dp0

REM === Kontrollera om .venv finns, annars skapa ===
IF NOT EXIST .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

REM === Aktivera venv ===
call .venv\Scripts\activate.bat

REM === Kontrollera om streamlit är installerat ===
where streamlit >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Installing requirements...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
)

REM === Kör test_ui.py ===
echo.
echo ✅ Environment ready. Starting Sensifilter UI...
echo.

REM === Döda ev. hängande streamlit-processer ===
for /f "tokens=2 delims=," %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq streamlit*" /FO CSV ^| find /I "python.exe"') do (
    taskkill /PID %%a /F >nul 2>&1
)

python -m streamlit run test_ui.py

REM === Återställ prompt ===
echo.
echo Streamlit UI closed. Press any key to exit.
pause
ENDLOCAL
