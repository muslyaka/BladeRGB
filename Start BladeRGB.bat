@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if exist ".venv\Scripts\pythonw.exe" goto run

echo =========================================
echo BladeRGB - FIRST START
echo =========================================
echo.
echo One-time local setup is starting.
echo No Rust, Cargo, Node.js or MSVC is required.
echo.

where py.exe >nul 2>nul
if not errorlevel 1 goto use_py

where python.exe >nul 2>nul
if not errorlevel 1 goto use_python

echo [ERROR] Python 3.11 or newer was not found.
echo Install Python from python.org and run this file again.
echo.
pause
exit /b 1

:use_py
py.exe -3 -m venv ".venv"
goto install

:use_python
python.exe -m venv ".venv"

:install
if errorlevel 1 goto fail

".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto fail

".venv\Scripts\python.exe" -m pip install -r "requirements.txt"
if errorlevel 1 goto fail

:run
start "" ".venv\Scripts\pythonw.exe" "main.py"
exit /b 0

:fail
echo.
echo [ERROR] First-start setup failed.
echo Run "Start BladeRGB Console.bat" for diagnostics.
echo.
pause
exit /b 1
