@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo   ========================================
echo      🐍 PyMaster - Python 编程学习平台
echo   ========================================
echo.
echo   [1/2] 检查依赖库...
pip install -r requirements.txt -q 2>nul
echo   [2/2] 启动服务器...
echo.
echo   ✅ 浏览器即将打开 http://127.0.0.1:5000
echo   📌 关闭此窗口即可退出程序
echo.
start "" http://127.0.0.1:5000
python app.py
pause
