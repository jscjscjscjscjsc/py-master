@echo off
chcp 936 >nul
cd /d "%~dp0"
title PyMaster 上线前自检

set "PORT=5000"
set "PY="
if exist "runtime\python\python.exe" set "PY=%~dp0runtime\python\python.exe"
if not defined PY if exist "runtime\venv\Scripts\python.exe" set "PY=%~dp0runtime\venv\Scripts\python.exe"

echo.
echo   ============================================================
echo      PyMaster 上线前自检
echo   ============================================================
echo.
echo   逐项检查上线要用的东西在不在、通不通。
echo.

if not defined PY (
  echo   [x] 找不到 Python 运行环境
  echo       —— 请先双击「一键上线.bat」完成环境准备。
  echo.
  pause
  exit /b 1
)
echo   [√] Python 运行环境：%PY%

"%PY%" "tools\preflight_check.py"
set "RC=%errorlevel%"

echo.
if "%RC%"=="0" (
  echo   自检通过，可以双击「一键上线.bat」了。
) else (
  echo   自检发现上面标 [x] 的问题，请先处理掉再上线。
)
echo.
pause
exit /b %RC%
