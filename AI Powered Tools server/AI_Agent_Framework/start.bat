@echo off
chcp 65001 >nul
title 🚀 Visual Novel Creator v2.0
color 0A

echo.
echo ╔════════════════════════════════════════════╗
echo ║     VISUAL NOVEL CREATOR 2.0              ║
echo ║     Professional Edition                  ║
echo ╚════════════════════════════════════════════╝
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
cd /d "C:\LM Studio\AI_Agent_Framework"

:: Create virtual environment if needed
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
)

:: Activate venv
call venv\Scripts\activate

:: Install/upgrade pip
python -m pip install --upgrade pip

:: Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

:: Install optional AI packages
echo 🤖 Installing AI enhancements...
pip install openai duckduckgo-search aiohttp

:: Start server
echo 🚀 Starting Visual Novel Creator...
echo.
echo 🌐 Web Interface: http://localhost:5000
echo 🛠️  Creator Tool: http://localhost:5000/creator
echo 🤖 Agents: Skipper & Kowalski
echo.

start "" "http://localhost:5000"
python server.py

pause