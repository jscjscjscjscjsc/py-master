@echo off
chcp 936 >nul
cd /d "%~dp0"
title PyMaster 一键上线

echo.
echo   ============================================================
echo      PyMaster 教学平台   服务器版一键上线
echo   ============================================================
echo.

if not exist "app.py" (
  echo   [错误] 本脚本必须和 app.py 放在同一个文件夹里。
  echo          请确认你解压的是完整的服务器版压缩包。
  echo.
  pause
  exit /b 1
)

REM ── 1. 检查管理员口令 ─────────────────────────────────────
if not exist ".env" (
  echo   [1/5] 首次运行，生成服务器配置文件 .env ...
  > ".env" echo # PyMaster 服务器配置（由「一键上线.bat」生成）
  >> ".env" echo # 管理员后台账号，务必改掉默认口令
  >> ".env" echo PYMASTER_ADMIN_USER=admin
  >> ".env" echo PYMASTER_ADMIN_PASSWORD=
) else (
  echo   [1/5] 已有 .env，沿用现有配置。
)

findstr /C:"PYMASTER_SERVER_MODE" ".env" >nul 2>nul
if errorlevel 1 (
  >> ".env" echo # 服务器模式：多人公网使用
  >> ".env" echo PYMASTER_SERVER_MODE=1
  >> ".env" echo # 在线运行/判题学生代码：公网默认关闭（服务器上无沙箱执行任意代码很危险）
  >> ".env" echo # 确实需要就在后台「系统设置」里打开，并同时开启安全沙箱
  >> ".env" echo PYMASTER_ALLOW_CODE_EXEC=0
  >> ".env" echo PYMASTER_SAFE_MODE=1
  >> ".env" echo # 并发线程数（十几个人用足够）
  >> ".env" echo PYMASTER_THREADS=16
)

REM 端口：默认 5000，可通过 PORT 环境变量覆盖
set "PORT=5000"
set "PYMASTER_SERVER_MODE=1"

REM ── 2. 开防火墙 ──────────────────────────────────────────
echo   [2/5] 放行 Windows 防火墙端口 %PORT% ...
netsh advfirewall firewall show rule name="PyMaster %PORT%" >nul 2>nul
if errorlevel 1 (
  netsh advfirewall firewall add rule name="PyMaster %PORT%" dir=in action=allow protocol=TCP localport=%PORT% >nul 2>nul
  if errorlevel 1 (
    echo         [!] 需要管理员权限才能改防火墙。请右键本文件选「以管理员身份运行」，
    echo             否则外面可能连不上（浏览器一直转圈）。
  ) else (
    echo         已放行 TCP %PORT%
  )
) else (
  echo         规则已存在，跳过。
)

REM ── 3. 准备运行环境 ──────────────────────────────────────
set "PY="

REM 随包 Python（服务器版压缩包自带，不需要装任何东西）
if exist "runtime\python\python.exe" set "PY=%~dp0runtime\python\python.exe"
if defined PY goto env_ready

if exist "runtime\python-embed.zip" (
  echo   [3/5] 解压随包 Python（只需一次）...
  if not exist "runtime\python" mkdir "runtime\python"
  tar -xf "runtime\python-embed.zip" -C "runtime\python" 2>nul
  if not exist "runtime\python\python.exe" powershell -NoProfile -Command "Expand-Archive -LiteralPath 'runtime\python-embed.zip' -DestinationPath 'runtime\python' -Force" >nul 2>nul
)
if exist "runtime\python\python.exe" set "PY=%~dp0runtime\python\python.exe"
if defined PY goto env_ready

echo   [3/5] 没有随包 Python，改用系统 Python 准备环境...
py -3 "tools\bootstrap_runtime.py"
if not errorlevel 1 goto use_venv
python "tools\bootstrap_runtime.py"
if not errorlevel 1 goto use_venv

echo.
echo   [错误] 没有可用的 Python。请使用完整服务器版压缩包（自带 Python）。
echo.
pause
exit /b 1

:use_venv
if exist "runtime\venv\Scripts\python.exe" set "PY=%~dp0runtime\venv\Scripts\python.exe"
if not defined PY (
  echo   [错误] 运行环境没有准备好，请查看上面的提示。
  pause
  exit /b 1
)
goto env_ready

:env_ready
echo   [3/5] 安装依赖（离线，不需要网络）...
"%PY%" "tools\bootstrap_runtime.py"
if errorlevel 1 (
  echo.
  echo   [错误] 依赖安装失败，请把上面的提示截图反馈。
  pause
  exit /b 1
)

REM ── 4. 显示访问地址 ──────────────────────────────────────
echo   [4/5] 探测本机 IP ...
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
  for /f "tokens=1" %%b in ("%%a") do echo         局域网/内网地址：%%b
)
echo         公网访问地址请看阿里云控制台的「公网 IP」（例如 8.152.3.17）
echo         完整地址形如： http://公网IP:%PORT%
echo.
echo         提示：阿里云「安全组」也要放行 TCP %PORT%，否则外面连不上。

REM ── 5. 启动 ──────────────────────────────────────────────
echo   [5/5] 启动服务 ...（关闭本窗口即停止服务）
echo.
echo   ------------------------------------------------------------
echo     上线后第一件事：打开 http://公网IP:%PORT%/admin
echo     默认管理员 admin / admin888，登录后立刻改口令
echo   ------------------------------------------------------------
echo.

set PYMASTER_OPEN_BROWSER=0
"%PY%" app.py
set "EXITCODE=%errorlevel%"

echo.
if not "%EXITCODE%"=="0" (
  echo   服务异常退出（代码 %EXITCODE%）。常见原因：
  echo     · %PORT% 端口被别的程序占用
  echo     · 杀毒软件拦截了 Python
  echo   上面的报错信息可以直接截图。
) else (
  echo   服务已停止。
)
echo.
pause
