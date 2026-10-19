@echo off
REM ---------------------------------------------------------------
REM  Mochi - AI Virtual Pet : one-click launcher for Windows
REM  Double-click this file (or run `run.bat` in a terminal).
REM ---------------------------------------------------------------
title Mochi - AI Virtual Pet
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [!] Python was not found on your PATH.
    echo     Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH".
    pause
    exit /b 1
)

echo [*] Installing / checking dependencies...
python -m pip install --quiet --disable-pip-version-check -r requirements.txt

echo [*] Starting Mochi on http://localhost:8501 ...
python -m streamlit run app.py --server.port 8501

pause
