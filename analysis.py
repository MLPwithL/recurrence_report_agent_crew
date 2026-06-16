"""阶段一：研报深度拆解与数据需求生成。

运行： `python analysis.py`

产物：
- outputs/summary.md
- outputs/data_requirements.md
- logs/agents/analysis_agent.md
"""

from __future__ import annotations

from crewai import Crew, Process

from agents import build_phase1_agents
from config_loader import OUTPUTS_DIR, RAW_DATA_DIR, TARGET_DIR, ensure_dirs, load_env, require_reports
from tasks import build_phase1_tasks
from tools import install_agent_logging, log_event, reset_agent_logs


def main() -> None:
    load_env()
    ensure_dirs()
    require_reports()

    # 阶段一只复位分析 Agent 的日志，其他 Agent 留待阶段二
    reset_agent_logs(["analysis_agent"])

    agents_map = build_phase1_agents()
    install_agent_logging(agents_map)

    analysis_agent = agents_map["analysis_agent"]
    tasks = build_phase1_tasks(analysis_agent)

    log_event(
        "analysis_agent",
        "阶段一启动",
        f"目标文件夹: `{TARGET_DIR}`\n任务数: {len(tasks)}",
    )

    crew = Crew(
        agents=[analysis_agent],
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    print("🚀 正在启动【阶段一】：研报深度拆解与数据需求分析...")
    result = crew.kickoff()
    log_event("analysis_agent", "阶段一结束", f"```\n{str(result)[:4000]}\n```")

    print("\n" + "=" * 60)
    print("✅ 阶段一执行完毕。")
    print(f"  - 研报摘要:   {OUTPUTS_DIR / 'summary.md'}")
    print(f"  - 数据需求:   {OUTPUTS_DIR / 'data_requirements.md'}")
    print(f"  - Agent 日志: logs/agents/analysis_agent.md")
    print()
    print("【人工干预】请将下载好的原始数据文件放入：")
    print(f"  {RAW_DATA_DIR}")
    print("准备就绪后运行：")
    print("  python main.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
