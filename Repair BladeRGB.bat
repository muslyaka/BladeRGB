@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Local environment is missing.
    echo Run "Start BladeRGB.bat" first.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install --upgrade -r "requirements.txt"
echo.
echo Repair complete.
pause
