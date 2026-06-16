"""阶段二：基于已就绪的原始数据，进行清洗、回测复现与总结。

运行： `python main.py`

前置条件：
- 已运行 `python analysis.py` 生成 summary.md 与 data_requirements.md
- 已把原始数据放入 `raw_data/`

产物：
- outputs/data_clean.py
- outputs/data_overview.md
- outputs/backtest.py
- outputs/final_report.md
- logs/agents/<each>.md
"""

from __future__ import annotations

from crewai import Crew, Process

from agents import build_phase2_agents
from config_loader import (
    OUTPUTS_DIR,
    RAW_DATA_DIR,
    TARGET_DIR,
    ensure_dirs,
    load_env,
    require_phase1_outputs,
    require_raw_data,
)
from tasks import build_phase2_tasks
from tools import install_agent_logging, log_event, reset_agent_logs


PHASE2_AGENT_NAMES = [
    "data_processing_agent",
    "reproduction_agent",
    "manager_agent",
    "summary_agent",
]


def main() -> None:
    load_env()
    ensure_dirs()
    require_phase1_outputs()
    require_raw_data()

    reset_agent_logs(PHASE2_AGENT_NAMES)

    agents_map = build_phase2_agents()
    install_agent_logging(agents_map)

    tasks = build_phase2_tasks(
        agents_map["data_processing_agent"],
        agents_map["reproduction_agent"],
        agents_map["manager_agent"],
        agents_map["summary_agent"],
    )

    for name in PHASE2_AGENT_NAMES:
        log_event(
            name,
            "阶段二启动",
            f"目标文件夹: `{TARGET_DIR}`\n原始数据: `{RAW_DATA_DIR}`\n任务数: {len(tasks)}",
        )

    crew = Crew(
        agents=[agents_map[n] for n in PHASE2_AGENT_NAMES],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    print("🚀 检测到原始数据，正在启动【阶段二】：清洗、回测与全盘审计...")
    result = crew.kickoff()

    for name in PHASE2_AGENT_NAMES:
        log_event(name, "阶段二结束", f"```\n{str(result)[:2000]}\n```")

    print("\n" + "=" * 60)
    print("✅ 阶段二执行完毕。")
    print(f"  - 清洗脚本:   {OUTPUTS_DIR / 'data_clean.py'}")
    print(f"  - 数据概述:   {OUTPUTS_DIR / 'data_overview.md'}")
    print(f"  - 回测脚本:   {OUTPUTS_DIR / 'backtest.py'}")
    print(f"  - 终极报告:   {OUTPUTS_DIR / 'final_report.md'}")
    print(f"  - Agent 日志: logs/agents/")
    print("=" * 60)


if __name__ == "__main__":
    main()
