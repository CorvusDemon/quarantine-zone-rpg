@echo off
cd /d "%~dp0"
echo ================================
echo  Quarantine Zone - Build Script
echo ================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found.
    pause
    exit /b 1
)

:: Install dependencies
echo [1/4] Installing dependencies...
call python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

:: Run tests before build
echo [2/4] Running tests...
call python -m pytest tests/ -v --tb=short
if errorlevel 1 (
    echo [ERROR] Tests failed! Fix errors first!
    pause
    exit /b 1
)

:: Clean old build
if exist "build" rd /s /q build
if exist "dist"  rd /s /q dist

:: Build exe
echo [3/4] Building executable...
call python -m PyInstaller ^
  --noconfirm ^
  --onedir ^
  --windowed ^
  --add-data "data;data" ^
  --add-data "assets;assets" ^
  --add-data "src;src" ^
  --hidden-import pygame ^
  --collect-all pygame ^
  --name QuarantineZone ^
  main.py

if exist "dist\QuarantineZone\QuarantineZone.exe" (
    echo ================================
    echo  [OK] Build successful!
    echo     Output: dist\QuarantineZone\
) else (
    echo [ERROR] Build failed. Check output above.
)

pause