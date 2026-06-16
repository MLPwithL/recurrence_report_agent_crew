"""统一配置加载器：负责路径、API Key、模型、YAML、skills 多文件读取。

所有脚本都从这里取配置，避免在主流程里到处读环境变量或硬编码路径。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, Optional

import yaml
from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# 1. 路径常量
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent

CONFIG_DIR = PROJECT_ROOT / "config"
SKILLS_DIR = PROJECT_ROOT / "skills"
TARGET_DIR = PROJECT_ROOT / "Report"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
RAW_DATA_DIR = PROJECT_ROOT / "raw_data"
LOGS_DIR = PROJECT_ROOT / "logs"
AGENT_LOG_DIR = LOGS_DIR / "agents"

# CrewAI tools enforce a filesystem safety boundary based on the process cwd.
# Keep cwd pinned to this copied project folder so tools never inherit a stale
# IDE or shell working directory from another machine/path.
TOOL_REPORT_DIR = "Report"
TOOL_OUTPUTS_DIR = "outputs"
TOOL_RAW_DATA_DIR = "raw_data"
TOOL_AGENT_LOG_DIR = str(Path("logs") / "agents")

# Agent 名 -> 留痕日志文件
AGENT_LOG_FILES: Dict[str, Path] = {
    "analysis_agent": AGENT_LOG_DIR / "analysis_agent.md",
    "data_processing_agent": AGENT_LOG_DIR / "data_processing_agent.md",
    "manager_agent": AGENT_LOG_DIR / "manager_agent.md",
    "reproduction_agent": AGENT_LOG_DIR / "reproduction_agent.md",
    "summary_agent": AGENT_LOG_DIR / "summary_agent.md",
}


def ensure_dirs() -> None:
    """确保运行时所需目录全部存在。"""
    os.chdir(PROJECT_ROOT)
    for d in (TARGET_DIR, OUTPUTS_DIR, RAW_DATA_DIR, LOGS_DIR, AGENT_LOG_DIR):
        d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# 2. 环境变量加载
# ---------------------------------------------------------------------------
def load_env() -> None:
    """加载 .env，优先顺序：.env > .env.proxy > .env.proxy.example > .env.example。"""
    candidates = [
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / ".env.proxy",
        PROJECT_ROOT / ".env.proxy.example",
        PROJECT_ROOT / ".env.example",
    ]
    for p in candidates:
        if p.exists():
            load_dotenv(p)
            return
    load_dotenv()  # fallback：从系统环境变量读


def _legacy_api_key() -> Optional[str]:
    legacy = PROJECT_ROOT / "api_key.txt"
    if legacy.exists():
        return legacy.read_text(encoding="utf-8").strip()
    return None


def get_openai_api_key() -> str:
    """读取 OpenAI-compatible API Key，兼容旧的 api_key.txt 模式。"""
    key = os.getenv("ROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if key:
        return key
    legacy = _legacy_api_key()
    if legacy:
        return legacy
    print("[ERROR] 未检测到 OpenAI-compatible API Key，请先配置 .env 或 api_key.txt。")
    sys.exit(1)


def get_anthropic_api_key() -> str:
    """读取 Anthropic API Key，兼容共用 ROUTER_API_KEY 和旧 api_key.txt 模式。"""
    key = os.getenv("ROUTER_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if key:
        return key
    legacy = _legacy_api_key()
    if legacy:
        return legacy
    print("[ERROR] 未检测到 Anthropic API Key，请先配置 .env 或 api_key.txt。")
    sys.exit(1)


def get_model_config() -> Dict[str, str]:
    """从环境变量读取模型与 BASE URL。"""
    return {
        "openai_api_base": os.getenv("OPENAI_API_BASE", "https://4router.net/v1"),
        "anthropic_base_url": os.getenv("ANTHROPIC_BASE_URL", "https://4Router.net"),
        "model_analysis": os.getenv("MODEL_ANALYSIS", "gpt-5.5"),
        "model_data_process": os.getenv("MODEL_DATA_PROCESS", "claude-opus-4-6"),
        "model_coder_api": os.getenv("MODEL_CODER_API") or os.getenv("MODEL_CODER", "gpt-5.4-mini"),
        "model_manager_summary": os.getenv("MODEL_MANAGER_SUMMARY", "gpt-5.4-mini"),
        "coder_execution_mode": os.getenv("CODER_EXECUTION_MODE", "API"),
    }


# ---------------------------------------------------------------------------
# 3. YAML 加载
# ---------------------------------------------------------------------------
def load_yaml(name: str) -> dict:
    path = CONFIG_DIR / name
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_agents_yaml() -> dict:
    return load_yaml("agents.yaml")


def load_tasks_yaml() -> dict:
    return load_yaml("tasks.yaml")


# ---------------------------------------------------------------------------
# 4. Skills 多文件聚合
# ---------------------------------------------------------------------------
def load_agent_skills(agent_name: str) -> str:
    """按 01_ 02_ 顺序读取 skills/<agent_name>/*.md 并拼接为一段 backstory 注入。

    若目录不存在，回退去读旧版的 skills/<agent_name>_skill.txt。
    """
    agent_dir = SKILLS_DIR / agent_name
    chunks = []

    if agent_dir.exists() and agent_dir.is_dir():
        files = sorted(p for p in agent_dir.glob("*.md") if p.is_file())
        for f in files:
            chunks.append(f"# === {f.name} ===\n{f.read_text(encoding='utf-8').strip()}")
    else:
        legacy_map = {
            "analysis_agent": "analysis_skill.txt",
            "data_processing_agent": "data_process_skill.txt",
            "manager_agent": "manager_skill.txt",
            "reproduction_agent": "reproduction_skill.txt",
            "summary_agent": "summary_skill.txt",
        }
        legacy = SKILLS_DIR / legacy_map.get(agent_name, "")
        if legacy.exists():
            chunks.append(legacy.read_text(encoding="utf-8").strip())

    if not chunks:
        return ""
    body = "\n\n".join(chunks)
    return f"\n\n# === 用户自定义技能约束 ({agent_name}) ===\n{body}"


# ---------------------------------------------------------------------------
# 5. 简单校验
# ---------------------------------------------------------------------------
def require_raw_data() -> None:
    if not RAW_DATA_DIR.exists() or not any(RAW_DATA_DIR.iterdir()):
        print(f"[ERROR] 未在 '{RAW_DATA_DIR}' 中检测到原始数据，请放入数据后再运行。")
        sys.exit(1)


def require_reports() -> None:
    report_suffixes = {".pdf", ".doc", ".docx"}
    if not TARGET_DIR.exists():
        print(f"[ERROR] 未检测到研报目录 '{TARGET_DIR}'，请先创建并放入 PDF / Word 研报。")
        sys.exit(1)
    reports = [p for p in TARGET_DIR.iterdir() if p.is_file() and p.suffix.lower() in report_suffixes]
    if not reports:
        print(f"[ERROR] 未在 '{TARGET_DIR}' 中检测到 PDF / Word 研报，请放入研报后再运行。")
        sys.exit(1)


def require_phase1_outputs() -> None:
    summary = OUTPUTS_DIR / "summary.md"
    reqs = OUTPUTS_DIR / "data_requirements.md"
    missing = [p.name for p in (summary, reqs) if not p.exists() or p.stat().st_size == 0]
    if missing:
        print(f"[ERROR] 阶段一产物缺失: {missing}，请先运行 `python analysis.py`。")
        sys.exit(1)
