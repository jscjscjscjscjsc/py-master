@echo off
chcp 936 >nul
cd /d "%~dp0"

REM 兜底：万一项目还放在子目录里（老版本的 发布版\），也照样能启动。
REM 正常情况下 app.py 就在本文件旁边，这一步会被跳过。
if not exist "app.py" if exist "%~dp0发布版\app.py" cd /d "%~dp0发布版"
if not exist "app.py" (
  echo   [错误] 这个启动脚本必须和 app.py 放在同一个文件夹里。
  echo          请把它放回 PyMaster 教学平台 目录下再双击。
  echo.
  pause
  exit /b 1
)

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

REM 解释器只认这两个固定相对路径，全部用 %~dp0 拼出来。
REM 不要用 for /f 去"捕获" python 的路径：中文用户名下，命令输出会经过
REM 代码页转换，捕回来的路径是乱码，cmd 就会报"系统找不到指定的路径"。

REM ① 随包 Python（完整压缩包自带）
if exist "runtime\python\python.exe" set "PY=%~dp0runtime\python\python.exe"
if defined PY goto ready

REM ② 上次用系统 Python 建好的虚拟环境
if exist "runtime\venv\Scripts\python.exe" set "PY=%~dp0runtime\venv\Scripts\python.exe"
if defined PY goto ready

REM ③ 包里有 Python 压缩包但还没解开：自己解，不依赖系统 Python
REM    （这是完整包的关键一步：用户机器上可以完全没有 Python）
if exist "runtime\python-embed.zip" (
  echo   [1/3] 正在解压随包 Python（只需一次）...
  if not exist "runtime\python" mkdir "runtime\python"
  tar -xf "runtime\python-embed.zip" -C "runtime\python" 2>nul
  if not exist "runtime\python\python.exe" powershell -NoProfile -Command "Expand-Archive -LiteralPath 'runtime\python-embed.zip' -DestinationPath 'runtime\python' -Force" >nul 2>nul
)
if exist "runtime\python\python.exe" set "PY=%~dp0runtime\python\python.exe"
if defined PY goto ready

REM ④ 精简包（不含 Python）：只能用系统 Python 建虚拟环境
echo   [1/3] 没有随包 Python，改用系统 Python 准备环境...
py -3 "tools\bootstrap_runtime.py"
if not errorlevel 1 goto system_ready
python "tools\bootstrap_runtime.py"
if not errorlevel 1 goto system_ready
goto need_python

:system_ready
if exist "runtime\venv\Scripts\python.exe" set "PY=%~dp0runtime\venv\Scripts\python.exe"
if not defined PY goto need_python
goto launch

:need_python
echo.
echo   [错误] 这台电脑上没有可用的 Python，这个压缩包里也没有附带。
echo.
echo   两个办法，任选其一：
echo     1. 下载"完整版"压缩包（自带 Python，不需要你装任何东西）
echo     2. 自己装 Python 3.12：https://www.python.org/downloads/
echo        安装时务必勾选 "Add python.exe to PATH"，装完重新双击本文件
goto end

:ready
echo   [1/3] 检查运行环境...
"%PY%" "tools\bootstrap_runtime.py"
if errorlevel 1 goto failed

:launch
echo   [2/3] 环境就绪，正在启动服务 http://127.0.0.1:5000
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
goto end

:failed
echo.
echo   [错误] 运行环境没有准备好，请把上面的提示截图反馈。

:end
echo.
pause
