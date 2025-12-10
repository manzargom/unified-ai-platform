@echo off
cd /d "C:\Fasttrack\video-editor"
echo Creating folder structure...

mkdir backend 2>nul
mkdir backend\ai_agents 2>nul
mkdir i18n 2>nul
mkdir assets 2>nul
mkdir assets\icons 2>nul
mkdir assets\transitions 2>nul
mkdir assets\demo_videos 2>nul

echo Structure created!
echo.
echo Next steps:
echo 1. Install requirements: pip install flask flask-cors opencv-python numpy
echo 2. Start server: python backend/server.py
echo 3. Open browser: http://localhost:5050
pause