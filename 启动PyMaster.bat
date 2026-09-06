@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo   ========================================
echo      PyMaster - Python 编程学习平台
echo   ========================================
echo.
echo   [1/3] 检查依赖库...
python -m pip install -r requirements.txt -q
if errorlevel 1 goto :error
echo   [2/3] 检查 AI 配置...
python setup_api.py
if errorlevel 1 goto :error
echo   [3/3] 启动 http://127.0.0.1:5000
start "" http://127.0.0.1:5000
python app.py
goto :end
:error
echo.
echo   启动失败，请检查上方错误信息。
:end
pause
