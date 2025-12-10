@echo off
chcp 65001 >nul
title 🚀 Visual Novel Creator
color 0A

echo.
echo ╔══════════════════════════════════════╗
echo ║     VISUAL NOVEL CREATOR            ║
echo ║     Auto-Launching Browser...       ║
echo ╚══════════════════════════════════════╝
echo.

cd /d "C:\LM Studio\AI_Agent_Framework"

echo 🚀 Installing dependencies...
echo Using: py -m pip install -r requirements.txt
py -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    echo.
    echo 💡 Trying alternative method...
    py -m pip install Flask==2.3.3 Flask-CORS==4.0.0 requests==2.31.0 Pillow==10.1.0
    if errorlevel 1 (
        echo ❌ Still failed.
        echo.
        echo Try: py -m pip install Flask requests Pillow --user
        pause
        exit /b 1
    )
)

echo ✅ Dependencies installed

echo 🚀 Starting server in background...
start "VN Server" cmd /c "py server.py"
if errorlevel 1 (
    echo ❌ Failed to start server
    pause
    exit /b 1
)

echo ⏳ Waiting for server to start (10 seconds)...
timeout /t 10 /nobreak >nul

echo 🌐 Opening browser to: http://localhost:5000
start "" "http://localhost:5000"

echo.
echo ✅ Done! Your browser should open automatically.
echo 💡 If not, manually go to: http://localhost:5000
echo.
echo 🖱️  Click the ORANGE "Creator's Tool" button
echo 🤖 Then click the robot icon for agent tools
echo.
echo Press any key to close this window...
pause >nul