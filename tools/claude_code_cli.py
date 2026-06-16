"""本地 Claude Code CLI 调用工具。

CrewAI 把它当作一个原生 Tool 注入给 reproduction_agent 使用。
"""

from __future__ import annotations

import subprocess

from crewai.tools import tool


@tool("Claude Code CLI Code Generator")
def claude_code_cli_tool(prompt: str) -> str:
    """调用本地 Claude Code CLI 生成复杂代码。"""
    try:
        result = subprocess.run(
            ["claude", "code", "--prompt", prompt],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except FileNotFoundError as e:
        return f"未找到 claude CLI 可执行文件，请先全局安装 Claude Code。详情: {e}"
    except subprocess.CalledProcessError as e:
        return f"Claude Code CLI 执行失败 (exit={e.returncode}): {e.stderr or e.stdout}"
    except Exception as e:  # noqa: BLE001
        return f"调用 Claude Code CLI 出现未知错误: {e}"
