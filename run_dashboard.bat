@echo off
setlocal
title Medicine Analytics - Dashboard (Flask)
cd /d "%~dp0"

echo ======================================================
echo   Medicine Price and Alternatives - Dashboard (Flask)
echo ======================================================
echo.

set "PY_CMD="
where py >nul 2>nul && py -3-64 --version >nul 2>nul && set "PY_CMD=py -3-64"
if not defined PY_CMD (
    if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PY_CMD="%LocalAppData%\Programs\Python\Python312\python.exe""
)
if not defined PY_CMD (
    where py >nul 2>nul && set "PY_CMD=py -3"
)
if not defined PY_CMD (
    where python >nul 2>nul && set "PY_CMD=python"
)
if not defined PY_CMD (
    echo [ERROR] No Python interpreter was found on this computer.
    echo         Install Python 3.11 or newer from https://www.python.org/downloads/
    echo         and tick "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)
echo [1/3] Interpreter:
%PY_CMD% --version

echo [2/3] Checking required packages...
%PY_CMD% -c "import flask" >nul 2>nul
if errorlevel 1 (
    echo       Flask is missing - installing it now ...
    %PY_CMD% -m pip install flask
    if errorlevel 1 (
        echo.
        echo [ERROR] Could not install Flask. Check your internet connection.
        echo.
        pause
        exit /b 1
    )
) else (
    echo       Flask is present.
)

echo [3/3] Starting the dashboard ...
echo.
%PY_CMD% run_dashboard.py

echo.
echo The dashboard server has stopped.
pause