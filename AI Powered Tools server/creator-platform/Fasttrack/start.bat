@echo off
chcp 65001 >nul
title 🎬 AI Video Editor

echo.
echo ========================================
echo        AI VIDEO EDITOR
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

:: Navigate to project
cd /d "C:\Fasttrack\video-editor"

:: Create virtual environment if needed
if not exist "venv" (
    echo 💡 Creating virtual environment...
    python -m venv venv
    echo 💡 Virtual environment created
)

:: Activate venv
call venv\Scripts\activate

:: Install/upgrade pip
python -m pip install --upgrade pip

:: Install dependencies
echo 💡 Installing dependencies...
pip install --r requirements.txt

echo.
echo ========================================
echo        STARTING VIDEO EDITOR
echo ========================================
echo.
echo 🌐 Web Interface: http://localhost:5050
echo 🤖 AI Features: Scene Detection
echo 📁 Projects saved in: uploads/
echo 💾 Exports saved in: exports/
echo.
echo 💡 Press Ctrl+C to stop the server
echo.

:: Start server
start "" "http://localhost:5050"
python backend/server.py

pause