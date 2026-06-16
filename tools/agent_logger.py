"""Agent 留痕日志：把每个 Agent 的输入输出和工具调用都写到独立的 .md 文件。

设计原则：
1. 一个 Agent 一个日志文件，路径见 config_loader.AGENT_LOG_FILES
2. 通过包装 Agent.execute_task / Tool 调用注入留痕，对 CrewAI 内部尽量无侵入
3. 即使版本不兼容，也只降级为 no-op，不阻断主流程
"""

from __future__ import annotations

import datetime as _dt
import threading
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

from config_loader import AGENT_LOG_DIR, AGENT_LOG_FILES, ensure_dirs


_LOCK = threading.Lock()


def _now() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _log_path_for(agent_name: str) -> Path:
    if agent_name in AGENT_LOG_FILES:
        return AGENT_LOG_FILES[agent_name]
    return AGENT_LOG_DIR / f"{agent_name}.md"


# ---------------------------------------------------------------------------
# 公共写入接口
# ---------------------------------------------------------------------------
def log_event(agent_name: str, title: str, body: str = "") -> None:
    """向某个 Agent 的日志追加一段事件记录（线程安全）。"""
    ensure_dirs()
    path = _log_path_for(agent_name)
    block = f"\n## [{_now()}] {title}\n\n"
    if body:
        block += body.rstrip() + "\n"
    with _LOCK:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(block)


def reset_agent_logs(agent_names: Optional[Iterable[str]] = None) -> None:
    """清空指定 Agent 的日志文件（默认全部）。"""
    ensure_dirs()
    targets = list(agent_names) if agent_names else list(AGENT_LOG_FILES.keys())
    for name in targets:
        path = _log_path_for(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# Agent 行为留痕：{name}\n\n初始化于 {_now()}。\n",
            encoding="utf-8",
        )


# ---------------------------------------------------------------------------
# Agent 包装器
# ---------------------------------------------------------------------------
class AgentLogger:
    """对 CrewAI Agent 进行最小侵入式包装，记录任务输入输出与工具调用。"""

    def __init__(self, agent: Any, agent_name: str) -> None:
        self.agent = agent
        self.agent_name = agent_name

    @staticmethod
    def _short(text: Any, limit: int = 4000) -> str:
        s = str(text) if text is not None else ""
        if len(s) <= limit:
            return s
        return s[:limit] + f"\n...[truncated {len(s) - limit} chars]"

    def install(self) -> None:
        self._patch_execute_task()
        self._patch_tools()

    # -- execute_task ------------------------------------------------------
    def _patch_execute_task(self) -> None:
        agent = self.agent
        name = self.agent_name
        original: Optional[Callable] = getattr(agent, "execute_task", None)
        if original is None or getattr(original, "_aurora_wrapped", False):
            return

        def wrapped(task, context=None, tools=None, *args, **kwargs):  # type: ignore[no-untyped-def]
            task_desc = getattr(task, "description", "<no description>")
            log_event(
                name,
                f"任务开始: {getattr(task, 'name', task_desc[:60])}",
                f"**任务描述**\n\n{self._short(task_desc)}\n",
            )
            try:
                result = original(task, context=context, tools=tools, *args, **kwargs)
            except Exception as e:  # noqa: BLE001
                log_event(name, "任务异常", f"```\n{e}\n```")
                raise
            log_event(
                name,
                "任务完成",
                f"**输出**\n\n```\n{self._short(result)}\n```",
            )
            return result

        wrapped._aurora_wrapped = True  # type: ignore[attr-defined]
        try:
            setattr(agent, "execute_task", wrapped)
        except Exception:  # noqa: BLE001
            # 某些 pydantic 模型不允许直接 setattr，忽略即可
            pass

    # -- tools -------------------------------------------------------------
    def _patch_tools(self) -> None:
        name = self.agent_name
        agent = self.agent
        tools = getattr(agent, "tools", None) or []
        for tool_obj in tools:
            run_attr = None
            for candidate in ("_run", "run", "func"):
                if hasattr(tool_obj, candidate):
                    run_attr = candidate
                    break
            if not run_attr:
                continue
            original = getattr(tool_obj, run_attr)
            if getattr(original, "_aurora_wrapped", False):
                continue

            tool_name = getattr(tool_obj, "name", tool_obj.__class__.__name__)

            def make_wrapper(orig: Callable, t_name: str) -> Callable:
                def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
                    log_event(
                        name,
                        f"调用工具: {t_name}",
                        f"args: `{AgentLogger._short(args, 1500)}`\n"
                        f"kwargs: `{AgentLogger._short(kwargs, 1500)}`",
                    )
                    try:
                        out = orig(*args, **kwargs)
                    except Exception as e:  # noqa: BLE001
                        log_event(name, f"工具异常: {t_name}", f"```\n{e}\n```")
                        raise
                    log_event(
                        name,
                        f"工具返回: {t_name}",
                        f"```\n{AgentLogger._short(out)}\n```",
                    )
                    return out

                wrapper._aurora_wrapped = True  # type: ignore[attr-defined]
                return wrapper

            try:
                setattr(tool_obj, run_attr, make_wrapper(original, tool_name))
            except Exception:  # noqa: BLE001
                continue


def install_agent_logging(agent_map: dict) -> None:
    """批量安装日志：传入 {agent_name: agent_instance}。"""
    ensure_dirs()
    for agent_name, agent in agent_map.items():
        try:
            AgentLogger(agent, agent_name).install()
            log_event(agent_name, "Agent 已挂载留痕器", "")
        except Exception as e:  # noqa: BLE001
            # 留痕本身不应影响主流程
            log_event(agent_name, "挂载留痕器失败", f"```\n{e}\n```")
