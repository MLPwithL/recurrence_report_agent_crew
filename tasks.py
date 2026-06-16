"""统一定义两个阶段所有 Task，并强制把产物落到正确路径。"""

from __future__ import annotations

from crewai import Task

from config_loader import OUTPUTS_DIR, load_tasks_yaml


def _t(name: str) -> dict:
    return load_tasks_yaml()[name]


# ---------------------------------------------------------------------------
# 阶段一：研报分析 + 数据需求
# ---------------------------------------------------------------------------
def build_phase1_tasks(analysis_agent) -> list[Task]:
    target = str(OUTPUTS_DIR)
    t_analysis = Task(
        config=_t("task_analysis"),
        agent=analysis_agent,
        output_file=f"{target}/summary.md",
    )
    t_data_requirements = Task(
        description=(
            "从研报中严格抽取出回测所需的具体数据字段、格式与频率，"
            "单独整理成一份纯净的 Markdown 表格。"
        ),
        expected_output="一份干净的、没有多余散文描述的 Markdown 数据清单表格。",
        agent=analysis_agent,
        output_file=f"{target}/data_requirements.md",
    )
    return [t_analysis, t_data_requirements]


# ---------------------------------------------------------------------------
# 阶段二：数据清洗 + 复现 + 总结
# ---------------------------------------------------------------------------
def build_phase2_tasks(
    data_processing_agent,
    reproduction_agent,
    manager_agent,
    summary_agent,
) -> list[Task]:
    target = str(OUTPUTS_DIR)

    t_data_process = Task(
        config=_t("task_data_process"),
        agent=data_processing_agent,
        output_file=f"{target}/data_clean.py",
    )

    t_manager_review_data = Task(
        config=_t("task_manager_review_data"),
        agent=manager_agent,
        output_file=f"{target}/data_overview.md",
    )

    t_reproduction = Task(
        config=_t("task_reproduction"),
        agent=reproduction_agent,
        output_file=f"{target}/backtest.py",
    )

    t_manager_review_code = Task(
        config=_t("task_manager_review_code"),
        agent=manager_agent,
    )

    t_summary = Task(
        config=_t("task_summary"),
        agent=summary_agent,
        output_file=f"{target}/final_report.md",
    )

    return [
        t_data_process,
        t_manager_review_data,
        t_reproduction,
        t_manager_review_code,
        t_summary,
    ]
