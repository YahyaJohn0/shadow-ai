#!/bin/bash

echo "🏗️  Shadow AI Installer Builder"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    exit 1
fi

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo "📦 Installing PyInstaller..."
    pip3 install pyinstaller
fi

# Install required packages
echo "📦 Installing required packages..."
pip3 install -r requirements_dist.txt

# Build the complete package
echo "🏗️  Building Shadow AI with graphical installer..."
python3 build_with_installer.py

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "🎉 Build completed successfully!"
echo "📦 Check the 'ShadowAI_Package' folder for the installer"