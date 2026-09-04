@echo off
setlocal EnableExtensions
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run "Start BladeRGB.bat" once before building.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean "BladeRGB.spec"
if errorlevel 1 (
    echo.
    echo [ERROR] Build failed.
    pause
    exit /b 1
)
echo.
echo =========================================
echo BUILD COMPLETE
echo =========================================
echo.
echo EXE:
echo   dist\BladeRGB\BladeRGB.exe
echo.
pause
