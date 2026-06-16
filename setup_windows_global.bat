@echo off
chcp 65001 >nul

echo ============================================================
echo 🤖 投研复现多智能体系统 - Windows 官方环境一键配置工具
echo ============================================================
echo.

set "PY_CMD="
set "TARGET_PY_PATH="

:: ============================================================
:: 1. 检查当前全局 python 是否存在，以及版本是否合规
:: ============================================================

echo [INFO] 正在检查当前全局 Python...

where python >nul 2>nul

if %errorlevel% equ 0 (
    python --version

    python -c "import sys; exit(0 if sys.version_info >= (3,11) and sys.version_info < (3,13) else 1)"

    if %errorlevel% equ 0 (
        echo [SUCCESS] 当前全局 Python 版本符合要求。
        set "PY_CMD=python"
        goto INSTALL_PACKAGES
    ) else (
        echo [WARNING] 当前全局 Python 版本不是 3.11 或 3.12。
        echo [INFO] 将检查系统中是否已安装 Python 3.11 / 3.12。
        echo.
    )
) else (
    echo [WARNING] 未检测到全局 python 命令。
    echo [INFO] 将检查系统中是否已安装 Python 3.11 / 3.12。
    echo.
)

:: ============================================================
:: 2. 检查 py launcher 是否存在
:: ============================================================

where py >nul 2>nul

if %errorlevel% neq 0 (
    echo [WARNING] 未检测到 Python Launcher: py。
    echo [INFO] 将尝试通过 winget 安装 Python 3.11。
    goto INSTALL_PYTHON
)

:: ============================================================
:: 3. 优先检查 Python 3.12
:: ============================================================

echo [INFO] 正在检查系统中是否存在 Python 3.12...

py -3.12 --version >nul 2>nul

if %errorlevel% equ 0 (
    echo [SUCCESS] 检测到 Python 3.12。
    set "PY_CMD=py -3.12"
    goto SET_GLOBAL_PYTHON
)

:: ============================================================
:: 4. 再检查 Python 3.11
:: ============================================================

echo [INFO] 正在检查系统中是否存在 Python 3.11...

py -3.11 --version >nul 2>nul

if %errorlevel% equ 0 (
    echo [SUCCESS] 检测到 Python 3.11。
    set "PY_CMD=py -3.11"
    goto SET_GLOBAL_PYTHON
)

echo [WARNING] 系统中未检测到 Python 3.11 或 Python 3.12。
goto INSTALL_PYTHON

:: ============================================================
:: 5. 将已存在的 Python 3.11 / 3.12 设置为当前用户全局 Python
:: ============================================================

:SET_GLOBAL_PYTHON

echo [INFO] 正在定位目标 Python 安装路径...

%PY_CMD% -c "import sys, os; print(os.path.dirname(sys.executable))" > "%TEMP%\target_python_path.txt"

if %errorlevel% neq 0 (
    echo [ERROR] 无法定位目标 Python 路径。
    pause
    exit /b 1
)

set /p TARGET_PY_PATH=<"%TEMP%\target_python_path.txt"

if "%TARGET_PY_PATH%"=="" (
    echo [ERROR] 目标 Python 路径为空。
    pause
    exit /b 1
)

echo [INFO] 目标 Python 路径：
echo %TARGET_PY_PATH%
echo.

echo [INFO] 正在将目标 Python 路径加入当前用户 PATH 前部...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$target='%TARGET_PY_PATH%';" ^
"$scripts=Join-Path $target 'Scripts';" ^
"$old=[Environment]::GetEnvironmentVariable('Path','User');" ^
"$parts=$old -split ';' | Where-Object { $_ -and ($_ -ne $target) -and ($_ -ne $scripts) };" ^
"$new=($target + ';' + $scripts + ';' + ($parts -join ';')).TrimEnd(';');" ^
"[Environment]::SetEnvironmentVariable('Path',$new,'User');"

if %errorlevel% neq 0 (
    echo [ERROR] 修改用户 PATH 失败。
    echo 请尝试以管理员身份运行终端，或手动调整环境变量。
    pause
    exit /b 1
)

echo [SUCCESS] 已将 Python 3.11 / 3.12 设置为当前用户全局优先版本。
echo.
echo [IMPORTANT] Windows PATH 修改后，当前终端可能不会立即刷新。
echo 请关闭当前终端，重新打开后再次运行本脚本。
pause
exit /b 0

:: ============================================================
:: 6. 如果没有合适 Python，则通过 winget 安装 Python 3.11
:: ============================================================

:INSTALL_PYTHON

echo [INFO] 正在检查 winget 是否可用...

where winget >nul 2>nul

if %errorlevel% neq 0 (
    echo [ERROR] 未检测到 winget。
    echo 请前往 python.org 手动安装 Python 3.11 或 Python 3.12。
    echo 安装完成后，请重新打开终端并再次运行本脚本。
    pause
    exit /b 1
)

echo [INFO] 正在通过 winget 安装 Python 3.11...

winget install Python.Python.3.11 --silent --accept-source-agreements --accept-package-agreements

if %errorlevel% neq 0 (
    echo [ERROR] Python 3.11 安装失败。
    echo 请前往 python.org 手动安装 Python 3.11 或 Python 3.12。
    pause
    exit /b 1
)

echo [SUCCESS] Python 3.11 安装成功。
echo [IMPORTANT] 请关闭当前终端，重新打开后再次运行本脚本，以刷新系统环境变量。
pause
exit /b 0

:: ============================================================
:: 7. 安装项目依赖
:: ============================================================

:INSTALL_PACKAGES

echo.
echo ============================================================
echo [INFO] 开始安装 CrewAI 项目依赖
echo ============================================================
echo.

echo [INFO] 当前使用的 Python：
%PY_CMD% --version
echo.

echo [INFO] 正在升级 pip...
%PY_CMD% -m pip install --upgrade pip

if %errorlevel% neq 0 (
    echo [ERROR] pip 升级失败。
    pause
    exit /b 1
)

echo.
echo [INFO] 正在安装核心框架：crewai...
%PY_CMD% -m pip install crewai

if %errorlevel% neq 0 (
    echo [ERROR] crewai 安装失败。
    pause
    exit /b 1
)

echo.
echo [INFO] 正在安装核心工具箱：crewai-tools...
%PY_CMD% -m pip install crewai-tools

if %errorlevel% neq 0 (
    echo [ERROR] crewai-tools 安装失败。
    pause
    exit /b 1
)

echo.
echo [INFO] 正在安装模型连接依赖：langchain-openai, langchain-anthropic...
%PY_CMD% -m pip install langchain-openai langchain-anthropic

if %errorlevel% neq 0 (
    echo [ERROR] langchain-openai 或 langchain-anthropic 安装失败。
    pause
    exit /b 1
)

echo.
echo [INFO] 正在安装基础依赖：python-dotenv, pyyaml, pypdf, docx2txt...
%PY_CMD% -m pip install python-dotenv pyyaml pypdf docx2txt

if %errorlevel% neq 0 (
    echo [ERROR] 基础依赖安装失败。
    pause
    exit /b 1
)

:: ============================================================
:: 8. 安装结果自检
:: ============================================================

echo.
echo ============================================================
echo [INFO] 正在进行安装结果自检
echo ============================================================
echo.

%PY_CMD% -c "import crewai; print('[CHECK] crewai OK')"

if %errorlevel% neq 0 (
    echo [ERROR] crewai 自检失败。
    pause
    exit /b 1
)

%PY_CMD% -c "import dotenv; print('[CHECK] python-dotenv OK')"

if %errorlevel% neq 0 (
    echo [ERROR] python-dotenv 自检失败。
    pause
    exit /b 1
)

%PY_CMD% -c "import yaml; print('[CHECK] pyyaml OK')"

if %errorlevel% neq 0 (
    echo [ERROR] pyyaml 自检失败。
    pause
    exit /b 1
)

%PY_CMD% -c "import pypdf; print('[CHECK] pypdf OK')"

if %errorlevel% neq 0 (
    echo [ERROR] pypdf 自检失败。
    pause
    exit /b 1
)

%PY_CMD% -c "import docx2txt; print('[CHECK] docx2txt OK')"

if %errorlevel% neq 0 (
    echo [ERROR] docx2txt 自检失败。
    pause
    exit /b 1
)

echo.
echo ============================================================
echo [SUCCESS] 官方运行环境已全部配置完毕！
echo ============================================================
echo.
echo 已安装核心组件：
echo - Python 3.11 或 Python 3.12
echo - pip
echo - crewai
echo - crewai-tools
echo - langchain-openai
echo - langchain-anthropic
echo - python-dotenv
echo - pyyaml
echo - pypdf
echo - docx2txt
echo.
echo 下一步：可以开始运行项目 Python 文件。
echo ============================================================

pause
exit /b 0