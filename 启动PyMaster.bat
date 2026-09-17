@echo off
chcp 936 >nul
cd /d "%~dp0"
title PyMaster 教学平台

echo.
echo   ============================================================
echo      PyMaster 教学平台    Python 自学系统
echo   ============================================================
echo.
echo   第一次启动会自动准备运行环境（约 1 分钟，之后秒开）。
echo   启动完成后浏览器会自动打开 http://127.0.0.1:5000
echo   关闭本窗口即停止服务。
echo.

set "PY="

REM ① 上次已经准备过：runtime\python-path.txt 里记着当时选定的解释器
if exist "runtime\python-path.txt" set /p PY=<"runtime\python-path.txt"
if defined PY if not exist "%PY%" set "PY="

REM ② 随包 Python（完整压缩包自带，用户不必自己装 Python）
if not defined PY if exist "runtime\python\python.exe" set "PY=%~dp0runtime\python\python.exe"

REM ③ 系统 Python：交给 bootstrap 建虚拟环境
if not defined PY (
  where py >nul 2>nul && set "PY=py -3"
)
if not defined PY (
  where python >nul 2>nul && set "PY=python"
)

if not defined PY (
  echo   [错误] 没有找到 Python，而且这个压缩包里也没有附带运行环境。
  echo.
  echo   两个办法，任选其一：
  echo     1. 重新下载完整版压缩包（自带 Python，不需要你装任何东西）
  echo     2. 自己装 Python 3.12：https://www.python.org/downloads/
  echo        安装时务必勾选 "Add python.exe to PATH"，装完重新双击本文件
  echo.
  goto end
)

echo   [1/2] 检查运行环境...
"%PY%" "tools\bootstrap_runtime.py"
if errorlevel 1 (
  echo.
  echo   [错误] 运行环境没有准备好，请把上面的提示截图反馈。
  goto end
)

if exist "runtime\python-path.txt" set /p PY=<"runtime\python-path.txt"

echo   [2/2] 正在启动服务 http://127.0.0.1:5000
echo.
echo   浏览器没自动打开的话，手动访问 http://127.0.0.1:5000 即可。
echo   首次使用请在网页里完成：注册账号 - 填写模型密钥 - 开始学习。
echo.

set PYMASTER_OPEN_BROWSER=1
"%PY%" app.py
set "EXITCODE=%errorlevel%"

echo.
if not "%EXITCODE%"=="0" (
  echo   [错误] 服务异常退出（代码 %EXITCODE%）。常见原因：
  echo     · 5000 端口被别的程序占用：关掉其它 PyMaster 窗口后重试
  echo     · 杀毒软件拦截了 Python：把本文件夹加入白名单
  echo     · 上面的报错信息可以直接截图反馈
) else (
  echo   服务已停止。
)

:end
echo.
pause
