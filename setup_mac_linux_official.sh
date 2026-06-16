#!/bin/bash

echo "============================================================"
echo "🤖 投研复现多智能体系统 - Mac/Linux 官方环境一键配置工具"
echo "============================================================"
echo

PY_CMD=""

# ============================================================
# 1. 检查当前全局 python3 是否存在，以及版本是否合规
# ============================================================

echo "[INFO] 正在检查当前全局 Python3..."

if command -v python3 &>/dev/null; then
    python3 --version

    python3 -c "import sys; exit(0 if sys.version_info >= (3,11) and sys.version_info < (3,13) else 1)"

    if [ $? -eq 0 ]; then
        echo "[SUCCESS] 当前全局 Python3 版本符合要求。"
        PY_CMD="python3"
    else
        echo "[WARNING] 当前全局 Python3 版本不是 3.11 或 3.12。"
        echo "[INFO] 将继续检查系统中是否存在 Python 3.11 / 3.12。"
        echo
    fi
else
    echo "[WARNING] 未检测到全局 python3 命令。"
    echo "[INFO] 将继续检查系统中是否存在 Python 3.11 / 3.12。"
    echo
fi

# ============================================================
# 2. 如果当前 python3 不合规，则检查 python3.12 / python3.11
# ============================================================

if [ -z "$PY_CMD" ]; then
    echo "[INFO] 正在检查系统中是否存在 Python 3.12..."

    if command -v python3.12 &>/dev/null; then
        python3.12 --version
        echo "[SUCCESS] 检测到 Python 3.12。"
        PY_CMD="python3.12"
    fi
fi

if [ -z "$PY_CMD" ]; then
    echo "[INFO] 正在检查系统中是否存在 Python 3.11..."

    if command -v python3.11 &>/dev/null; then
        python3.11 --version
        echo "[SUCCESS] 检测到 Python 3.11。"
        PY_CMD="python3.11"
    fi
fi

# ============================================================
# 3. 如果 Mac 没有合适 Python，则尝试通过 Homebrew 安装 Python 3.12
# ============================================================

if [ -z "$PY_CMD" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "[WARNING] 当前系统未检测到 Python 3.11 或 Python 3.12。"
        echo "[INFO] 当前系统为 macOS，将检查 Homebrew 是否可用..."

        if ! command -v brew &>/dev/null; then
            echo "[ERROR] 未检测到 Homebrew。"
            echo "请先安装 Homebrew，或前往 python.org 手动安装 Python 3.11 / 3.12。"
            echo
            echo "Homebrew 安装地址："
            echo "https://brew.sh/"
            exit 1
        fi

        echo "[INFO] 正在通过 Homebrew 安装 Python 3.12..."
        brew install python@3.12

        if [ $? -ne 0 ]; then
            echo "[ERROR] Python 3.12 安装失败。"
            echo "请前往 python.org 手动安装 Python 3.11 / 3.12。"
            exit 1
        fi

        echo "[SUCCESS] Python 3.12 安装完成。"

        if command -v python3.12 &>/dev/null; then
            PY_CMD="python3.12"
        else
            echo "[ERROR] 安装后仍无法检测到 python3.12。"
            echo "请关闭终端后重新打开，再次运行本脚本。"
            exit 1
        fi
    else
        echo "[ERROR] 当前 Linux 系统未检测到 Python 3.11 或 Python 3.12。"
        echo
        echo "请使用您的系统包管理器安装 Python 3.11 或 Python 3.12。"
        echo
        echo "Ubuntu / Debian 示例："
        echo "sudo apt update"
        echo "sudo apt install python3.11 python3.11-venv python3.11-dev"
        echo
        echo "Fedora 示例："
        echo "sudo dnf install python3.11 python3.11-devel"
        echo
        echo "Arch 示例："
        echo "sudo pacman -S python"
        exit 1
    fi
fi

# ============================================================
# 4. 输出当前实际使用的 Python
# ============================================================

echo
echo "============================================================"
echo "[INFO] 当前将使用以下 Python 环境"
echo "============================================================"
$PY_CMD --version
echo "Python 命令：$PY_CMD"
echo

# ============================================================
# 5. 升级 pip
# ============================================================

echo "[INFO] 正在升级 pip..."
$PY_CMD -m pip install --upgrade pip

if [ $? -ne 0 ]; then
    echo "[ERROR] pip 升级失败。"
    echo "请检查网络连接、Python 安装状态，或尝试手动执行："
    echo "$PY_CMD -m pip install --upgrade pip"
    exit 1
fi

echo "[SUCCESS] pip 升级完成。"
echo

# ============================================================
# 6. 安装 CrewAI 核心框架
# ============================================================

echo "[INFO] 正在安装核心框架：crewai..."
$PY_CMD -m pip install crewai

if [ $? -ne 0 ]; then
    echo "[ERROR] crewai 安装失败。"
    exit 1
fi

echo "[SUCCESS] crewai 安装完成。"
echo

# ============================================================
# 7. 安装 CrewAI 工具箱
# ============================================================

echo "[INFO] 正在安装核心工具箱：crewai-tools..."
$PY_CMD -m pip install crewai-tools

if [ $? -ne 0 ]; then
    echo "[ERROR] crewai-tools 安装失败。"
    exit 1
fi

echo "[SUCCESS] crewai-tools 安装完成。"
echo

# ============================================================
# 8. 安装模型连接相关依赖
# ============================================================

echo "[INFO] 正在安装模型连接依赖：langchain-openai, langchain-anthropic..."
$PY_CMD -m pip install langchain-openai langchain-anthropic

if [ $? -ne 0 ]; then
    echo "[ERROR] langchain-openai 或 langchain-anthropic 安装失败。"
    exit 1
fi

echo "[SUCCESS] 模型连接依赖安装完成。"
echo

# ============================================================
# 9. 安装文档解析与配置读取依赖
# ============================================================

echo "[INFO] 正在安装基础依赖：python-dotenv, pyyaml, pypdf, docx2txt..."
$PY_CMD -m pip install python-dotenv pyyaml pypdf docx2txt

if [ $? -ne 0 ]; then
    echo "[ERROR] 基础依赖安装失败。"
    exit 1
fi

echo "[SUCCESS] 基础依赖安装完成。"
echo

# ============================================================
# 10. 安装结果自检
# ============================================================

echo "============================================================"
echo "[INFO] 正在进行安装结果自检"
echo "============================================================"
echo

$PY_CMD -c "import crewai; print('[CHECK] crewai OK')"

if [ $? -ne 0 ]; then
    echo "[ERROR] crewai 自检失败。"
    exit 1
fi

$PY_CMD -c "import dotenv; print('[CHECK] python-dotenv OK')"

if [ $? -ne 0 ]; then
    echo "[ERROR] python-dotenv 自检失败。"
    exit 1
fi

$PY_CMD -c "import yaml; print('[CHECK] pyyaml OK')"

if [ $? -ne 0 ]; then
    echo "[ERROR] pyyaml 自检失败。"
    exit 1
fi

$PY_CMD -c "import pypdf; print('[CHECK] pypdf OK')"

if [ $? -ne 0 ]; then
    echo "[ERROR] pypdf 自检失败。"
    exit 1
fi

$PY_CMD -c "import docx2txt; print('[CHECK] docx2txt OK')"

if [ $? -ne 0 ]; then
    echo "[ERROR] docx2txt 自检失败。"
    exit 1
fi

echo
echo "============================================================"
echo "[SUCCESS] 官方运行环境已全部配置完毕！"
echo "============================================================"
echo
echo "已安装核心组件："
echo "- Python 3.11 或 Python 3.12"
echo "- pip"
echo "- crewai"
echo "- crewai-tools"
echo "- langchain-openai"
echo "- langchain-anthropic"
echo "- python-dotenv"
echo "- pyyaml"
echo "- pypdf"
echo "- docx2txt"
echo
echo "下一步：可以开始运行项目 Python 文件。"
echo "============================================================"