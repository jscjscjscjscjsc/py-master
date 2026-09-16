@echo off
chcp 936 >nul
cd /d "%~dp0"
title PyMaster 教学平台 (新版 · 39 章)

echo.
echo   ================================================
echo      PyMaster 教学平台    新版 · 39 章 / 400 知识点
echo   ================================================
echo.
echo   启动目录: %CD%
echo.
echo   [提示] 新版在这里。原版总包是旧的 9 章版本，别启动那个。
echo.

REM 依赖检查：库齐了就不联网跑 pip，启动更快
python -c "import flask, edge_tts" 2>nul
if errorlevel 1 (
  echo   [1/3] 缺少依赖库，正在安装...
  python -m pip install -r requirements.txt -q
  if errorlevel 1 goto error
) else (
  echo   [1/3] 依赖库已就绪
)

echo   [2/3] 检查 AI 配置...
python setup_api.py
if errorlevel 1 goto error

REM 先起服务，6 秒后再开浏览器。
REM 顺序很重要：先开浏览器的话，5000 端口上可能还挂着上次的旧进程，
REM 浏览器会先渲染出旧页面，看起来像"改动没生效"。
echo   [3/3] 启动服务 http://127.0.0.1:5000
echo.
echo   启动完成后浏览器会自动打开。按 Ctrl+C 停止服务。
echo.
start "" /min cmd /c "timeout /t 6 /nobreak >nul & start http://127.0.0.1:5000"
python app.py
goto end

:error
echo.
echo   [错误] 启动失败，请查看上方报错信息。
echo.

:end
pause
