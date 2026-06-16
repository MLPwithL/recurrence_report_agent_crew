"""统一定义所有 Agent，并按需挂载工具、Skill 与 LLM。"""

from __future__ import annotations

from typing import Optional

from crewai import Agent, LLM
from crewai_tools import DirectoryReadTool

from config_loader import (
    TOOL_AGENT_LOG_DIR,
    TOOL_OUTPUTS_DIR,
    TOOL_RAW_DATA_DIR,
    TOOL_REPORT_DIR,
    get_anthropic_api_key,
    get_model_config,
    get_openai_api_key,
    load_agents_yaml,
    load_agent_skills,
)
from tools import ReportReaderTool, claude_code_cli_tool, codex_cli_tool


# ---------------------------------------------------------------------------
# LLM 工厂
# ---------------------------------------------------------------------------
def _openai_llm(model_name: str, temperature: float = 0.3) -> LLM:
    cfg = get_model_config()
    return LLM(
        model=model_name,
        api_key=get_openai_api_key(),
        base_url=cfg["openai_api_base"] or None,
        temperature=temperature,
    )


def _anthropic_llm(model_name: str, temperature: float = 0.1) -> LLM:
    cfg = get_model_config()
    return LLM(
        model=model_name,
        api_key=get_anthropic_api_key(),
        base_url=cfg["anthropic_base_url"] or None,
        temperature=temperature,
    )


# ---------------------------------------------------------------------------
# Agent 构造工具
# ---------------------------------------------------------------------------
def _build_agent(name: str, llm, tools: Optional[list] = None, **extra) -> Agent:
    cfg = load_agents_yaml()[name]
    backstory = cfg.get("backstory", "") + load_agent_skills(name)
    return Agent(
        role=cfg["role"],
        goal=cfg["goal"],
        backstory=backstory,
        llm=llm,
        tools=tools or [],
        verbose=True,
        **extra,
    )


# ---------------------------------------------------------------------------
# 阶段一：分析 Agent
# ---------------------------------------------------------------------------
def build_analysis_agent() -> Agent:
    cfg = get_model_config()
    tools = [
        DirectoryReadTool(directory=TOOL_REPORT_DIR),
        ReportReaderTool(),
    ]
    return _build_agent(
        "analysis_agent",
        llm=_openai_llm(cfg["model_analysis"], temperature=0.3),
        tools=tools,
    )


# ---------------------------------------------------------------------------
# 阶段二：数据 / 复现 / 主管 / 总结 Agent
# ---------------------------------------------------------------------------
def build_data_processing_agent() -> Agent:
    cfg = get_model_config()
    raw_tool = DirectoryReadTool(directory=TOOL_RAW_DATA_DIR)
    outputs_tool = DirectoryReadTool(directory=TOOL_OUTPUTS_DIR)
    return _build_agent(
        "data_processing_agent",
        llm=_anthropic_llm(cfg["model_data_process"], temperature=0.1),
        tools=[raw_tool, outputs_tool],
    )


def build_reproduction_agent() -> Agent:
    cfg = get_model_config()
    mode = (cfg["coder_execution_mode"] or "API").upper()
    outputs_tool = DirectoryReadTool(directory=TOOL_OUTPUTS_DIR)
    raw_tool = DirectoryReadTool(directory=TOOL_RAW_DATA_DIR)
    tools = [outputs_tool, raw_tool]
    if mode == "CLI_CODEX":
        tools.append(codex_cli_tool)
    elif mode in ("CLI_CLAUDE", "CLI_CLAUDE_CODE"):
        tools.append(claude_code_cli_tool)
    llm = _openai_llm(cfg["model_coder_api"], temperature=0.2)
    return _build_agent("reproduction_agent", llm=llm, tools=tools)


def build_manager_agent() -> Agent:
    cfg = get_model_config()
    return _build_agent(
        "manager_agent",
        llm=_openai_llm(cfg["model_manager_summary"], temperature=0.4),
        tools=[
            DirectoryReadTool(directory=TOOL_OUTPUTS_DIR),
            DirectoryReadTool(directory=TOOL_RAW_DATA_DIR),
        ],
        allow_code_execution=True,
        allow_delegation=True,
    )


def build_summary_agent() -> Agent:
    cfg = get_model_config()
    return _build_agent(
        "summary_agent",
        llm=_openai_llm(cfg["model_manager_summary"], temperature=0.5),
        tools=[
            DirectoryReadTool(directory=TOOL_OUTPUTS_DIR),
            DirectoryReadTool(directory=TOOL_AGENT_LOG_DIR),
        ],
    )


# ---------------------------------------------------------------------------
# 一次性构造全部 Agent（按需调用，避免阶段一就触发 Anthropic 初始化）
# ---------------------------------------------------------------------------
def build_phase1_agents() -> dict:
    return {"analysis_agent": build_analysis_agent()}


def build_phase2_agents() -> dict:
    return {
        "data_processing_agent": build_data_processing_agent(),
        "reproduction_agent": build_reproduction_agent(),
        "manager_agent": build_manager_agent(),
        "summary_agent": build_summary_agent(),
    }
