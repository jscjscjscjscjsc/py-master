@echo off
chcp 936 >nul
title PyMaster 服务器端诊断与修复

REM ── 自动请求管理员权限（开防火墙必须）──
net session >nul 2>&1
if errorlevel 1 (
  echo.
  echo   需要管理员权限，正在重新启动...
  powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs" >nul 2>nul
  exit /b
)

echo.
echo   ============================================================
echo      PyMaster 服务器端诊断与修复
echo   ============================================================
echo.
echo   会依次做三件事：
echo     1. 放行 Windows 防火墙的 5000 端口（安全组放行后仍连不上，多半卡在这里）
echo     2. 检查 PyMaster 服务是否在运行
echo     3. 没运行就尝试启动
echo.

REM ── 1. 防火墙 ─────────────────────────────────────────────
echo   [1/3] 放行 Windows 防火墙 5000 ...
netsh advfirewall firewall delete rule name="PyMaster 5000" >nul 2>nul
netsh advfirewall firewall add rule name="PyMaster 5000" dir=in action=allow protocol=TCP localport=5000 >nul 2>nul
if errorlevel 1 (
  echo         [x] 添加失败
) else (
  echo         [√] 已放行 TCP 5000 入站
)

REM ── 2. 服务是否在监听 ────────────────────────────────────
echo.
echo   [2/3] 检查 5000 端口监听状态 ...
netstat -ano | findstr ":5000" | findstr LISTEN >nul 2>nul
if not errorlevel 1 (
  echo         [√] 有程序正在监听 5000：
  netstat -ano | findstr ":5000" | findstr LISTEN
  goto summary
)
echo         [x] 没有程序监听 5000 —— PyMaster 服务没在运行

REM ── 3. 尝试启动 ──────────────────────────────────────────
echo.
echo   [3/3] 查找并启动 PyMaster ...

set "PMDIR="
if exist "%~dp0app.py" set "PMDIR=%~dp0"
if not defined PMDIR if exist "D:\PyMaster\app.py" set "PMDIR=D:\PyMaster\"
if not defined PMDIR if exist "C:\PyMaster\app.py" set "PMDIR=C:\PyMaster\"
if not defined PMDIR for %%d in (C D E F G) do (
  if not defined PMDIR if exist "%%d:\" (
    for /f "delims=" %%f in ('dir /b /s "%%d:\app.py" 2^>nul ^| findstr /i "pymaster"') do (
      if not defined PMDIR set "PMDIR=%%~dpf"
    )
  )
)

if not defined PMDIR (
  echo         [x] 常见位置没找到 PyMaster 的 app.py
  echo             请手动进入解压目录，双击「一键上线.bat」
  goto summary
)
echo         找到目录：%PMDIR%

if exist "%PMDIR%一键上线.bat" (
  echo         正在启动（会弹出一个新窗口，那个窗口不能关）...
  start "PyMaster" cmd /c ""%PMDIR%一键上线.bat""
  echo         等待服务起来（最多 45 秒）...
  for /l %%i in (1,1,15) do (
    timeout /t 3 >nul
    netstat -ano | findstr ":5000" | findstr LISTEN >nul 2>nul
    if not errorlevel 1 (
      echo         [√] 服务已启动并在监听 5000
      goto summary
    )
  )
  echo         [!] 45 秒内仍未见监听，请到那个窗口看报错信息
) else if exist "%PMDIR%app.py" (
  echo         目录里没有「一键上线.bat」，尝试直接用随包 Python 启动...
  if exist "%PMDIR%runtime\python\python.exe" (
    start "PyMaster" cmd /c "cd /d "%PMDIR%" && set PYMASTER_SERVER_MODE=1 && set PORT=5000 && "%PMDIR%runtime\python\python.exe" app.py"
    echo         已尝试启动，等待 20 秒...
    timeout /t 20 >nul
    netstat -ano | findstr ":5000" | findstr LISTEN && echo         [√] 服务已启动
  ) else (
    echo         [x] 找不到随包 Python，请手动启动
  )
) else (
  echo         [x] 该目录没有可用的启动方式
)

:summary
echo.
echo   ────────────────────────────────────────────────────────
echo   本机 IPv4 地址：
ipconfig | findstr /C:"IPv4"
echo   ────────────────────────────────────────────────────────
echo.
echo   本机侧做完后，还需要在阿里云控制台放行安全组 TCP 5000，
echo   外部才能访问。地址形如： http://公网IP:5000
echo.
pause
