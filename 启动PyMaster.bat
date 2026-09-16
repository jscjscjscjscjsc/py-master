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

REM 依赖检查：库齐了就不联网跑 pip，启动更快
python -c "import flask, edge_tts" 2>nul
if errorlevel 1 (
  echo   [1/2] 缺少依赖库，正在安装...
  python -m pip install -r requirements.txt -q
  if errorlevel 1 (
    echo         默认源太慢，换清华镜像重试...
    python -m pip install -r requirements.txt -q -i https://pypi.tuna.tsinghua.edu.cn/simple
    if errorlevel 1 goto error
  )
) else (
  echo   [1/2] 依赖库已就绪
)

REM 账号注册与模型配置都在网页里完成，不再让用户对着黑窗口填。
REM 首次打开会自动进入配置向导（/setup）。
echo   [2/2] 启动服务 http://127.0.0.1:5000
echo.
echo   浏览器会自动打开。
echo   首次使用请在网页里：注册账号 - 填模型地址与密钥 - 开始学习。
echo   按 Ctrl+C 停止服务。
echo.
start "" /min cmd /c "timeout /t 6 /nobreak >nul & start http://127.0.0.1:5000"
python app.py
goto end

:error
echo.
echo   [错误] 依赖安装失败，请检查网络后重试。
echo.

:end
pause
