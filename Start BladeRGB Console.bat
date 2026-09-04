@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Local environment is missing.
    echo Run "Start BladeRGB.bat" first.
    echo.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "main.py"
echo.
echo BladeRGB exited with code %ERRORLEVEL%.
echo.
pause
