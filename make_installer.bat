@echo off
chcp 65001 >nul
title Shadow AI Installer Builder

echo.
echo 🏗️  Shadow AI Installer Builder
echo ================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

:: Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing PyInstaller...
    pip install pyinstaller
)

:: Install required packages
echo 📦 Installing required packages...
pip install -r requirements_dist.txt

:: Build the complete package
echo 🏗️  Building Shadow AI with graphical installer...
python build_with_installer.py

if errorlevel 1 (
    echo.
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo.
echo 🎉 Build completed successfully!
echo 📦 Check the 'ShadowAI_Package' folder for the installer
echo.
pause