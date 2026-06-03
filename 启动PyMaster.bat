@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo   🐍 PyMaster 启动中...
echo.
start "" http://127.0.0.1:5000
python app.py
pause
