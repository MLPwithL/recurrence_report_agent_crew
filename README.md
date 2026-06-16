# 🚀 多智能体研报复现与自动量化回测系统（CrewAI 架构）

本项目是一个基于 **CrewAI** 的多 Agent 协作投研系统，目标是把一篇研究报告自动跑成一条完整的复现流水线：

```text
研报解析 → 数据需求提取 → 数据清洗代码生成 → 数据清洗审查 → 回测代码生成 → 回测审查 → 最终总结报告
```

用户只需要做这 7 件事：

```text
1. 配置运行环境
2. 填写 API Key
3. 放入研究报告
4. 运行 analysis.py
5. 根据 outputs/data_requirements.md 准备并放入原始数据
6. 运行 main.py
7. 查看最终输出与每个 Agent 的留痕日志
```

---

## 1. 项目运行逻辑

本项目分为两个主要阶段。

### 阶段一：研报分析阶段

运行入口：

```bash
python analysis.py
```

由 **分析 Agent** 负责，主要完成：

```text
1. 读取 Report/ 文件夹中的 PDF / Word 研报
2. 分析研报核心思想
3. 提取策略逻辑
4. 提取回测方法
5. 提取所需数据字段、频率和格式
```

阶段一产物：

| 文件                                       | 作用                       |
| ---------------------------------------- | ------------------------ |
| `outputs/summary.md`                     | 研报核心摘要、策略逻辑、研究方法总结       |
| `outputs/data_requirements.md`           | 回测复现所需的数据字段、频率、格式和说明     |
| `logs/agents/analysis_agent.md`          | 阶段一分析 Agent 的输入输出与工具调用留痕 |

阶段一结束后，请阅读 `outputs/data_requirements.md`，根据其中的数据需求手动准备原始数据，放入：

```text
raw_data/
```

### 阶段二：数据清洗、回测复现与总结阶段

确认 `raw_data/` 不为空后，运行：

```bash
python main.py
```

由 4 个 Agent 协作完成：

```text
1. data_processing_agent 读取 outputs/data_requirements.md + raw_data/ 原始数据，生成 outputs/data_clean.py
2. manager_agent 检查数据清洗代码，输出 outputs/data_overview.md
3. reproduction_agent 编写回测代码 outputs/backtest.py
4. manager_agent 审查回测代码并执行验证
5. summary_agent 汇总全流程，生成 outputs/final_report.md
```

阶段二产物：

| 文件                                  | 作用            |
| ----------------------------------- | ------------- |
| `outputs/data_clean.py`             | 数据清洗脚本        |
| `outputs/data_overview.md`          | 数据处理与审查报告     |
| `outputs/backtest.py`               | 策略复现与回测代码     |
| `outputs/final_report.md`           | 全流程最终总结报告     |
| `logs/agents/<agent_name>.md`       | 阶段二每个 Agent 的留痕日志 |

---

## 2. 项目目录结构

```text
recurrence_report_agent/
│
├── analysis.py             # 阶段一入口：研报分析 + 数据需求
├── main.py                 # 阶段二入口：清洗 + 复现 + 总结
├── agents.py               # 5 个 Agent 的统一构造器
├── tasks.py                # 阶段一/阶段二的 Task 定义
├── config_loader.py        # 路径、.env、API Key、模型、YAML、Skills 多文件加载
│
├── requirements.txt
├── README.md
│
├── .env.example            # 官方直连配置模板
├── .env.proxy.example      # 4Router 中转站配置模板
├── .env                    # 用户实际使用的环境变量
│
├── setup_windows_global.bat
├── setup_mac_linux_official.sh
├── setup_env.bat / .ps1 / .sh
│
├── config/
│   ├── agents.yaml         # 各 Agent 角色 / 目标 / 基础 backstory
│   └── tasks.yaml          # 各 Task 描述与期望输出
│
├── tools/
│   ├── __init__.py
│   ├── codex_cli.py        # 本地 Codex CLI 调用工具
│   ├── claude_code_cli.py  # 本地 Claude Code CLI 调用工具
│   └── agent_logger.py     # Agent 行为留痕器
│
├── skills/
│   ├── analysis_agent/
│   │   ├── 01_base_rules.md
│   │   ├── 02_report_reading_rules.md
│   │   └── 03_output_rules.md
│   ├── data_processing_agent/
│   │   ├── 01_base_rules.md
│   │   ├── 02_data_cleaning_rules.md
│   │   ├── 03_missing_value_rules.md
│   │   ├── 04_exception_rules.md
│   │   └── 05_output_rules.md
│   ├── manager_agent/
│   │   ├── 01_base_rules.md
│   │   ├── 02_code_review_rules.md
│   │   ├── 03_execution_check_rules.md
│   │   └── 04_output_rules.md
│   ├── reproduction_agent/
│   │   ├── 01_base_rules.md
│   │   ├── 02_backtest_rules.md
│   │   ├── 03_codex_cli_rules.md
│   │   ├── 04_bias_control_rules.md
│   │   └── 05_output_rules.md
│   └── summary_agent/
│       ├── 01_base_rules.md
│       ├── 02_summary_rules.md
│       └── 03_output_rules.md
│
├── logs/
│   └── agents/
│       ├── analysis_agent.md
│       ├── data_processing_agent.md
│       ├── manager_agent.md
│       ├── reproduction_agent.md
│       └── summary_agent.md
│
├── Report/
│   └── (研报 PDF / Word 文件)
│
├── raw_data/
│   └── (用户手动放入的原始数据)
│
└── outputs/
    ├── summary.md
    ├── data_requirements.md
    ├── data_clean.py
    ├── data_overview.md
    ├── codex_reproduction_log.md
    ├── backtest.py
    ├── backtest_result.md
    ├── backtest_review.md
    └── final_report.md
```

注意：

```text
1. 研报文件直接放在 Report/ 下。
2. 原始数据必须放入 raw_data/。
3. config/ 必须包含 agents.yaml 与 tasks.yaml。
4. skills/<agent_name>/ 下的 .md 文件会按文件名升序自动加载并拼接进 Agent 的 backstory。
5. logs/agents/ 由系统自动创建，无需手动维护。
```

---

## 3. 环境准备

推荐 Python 版本：

```text
Python 3.11 / Python 3.12
```

不建议：

```text
Python 3.10 及以下
Python 3.13 及以上
```

CrewAI、LangChain、Pydantic 与文档解析依赖在 3.11 / 3.12 上最稳定。

---

## 4. Windows 一键配置

```bat
setup_windows_global.bat
```

脚本会自动：

```text
1. 检查 Python 是否存在
2. 检查版本是否为 3.11 / 3.12
3. 安装 CrewAI / CrewAI Tools
4. 安装 LangChain OpenAI / Anthropic 连接依赖
5. 安装 PDF / Word 解析依赖
6. 执行 import 自检
```

如果脚本修改了 PATH，请关闭并重开终端。

---

## 5. Mac / Linux 一键配置

```bash
chmod +x setup_mac_linux_official.sh
./setup_mac_linux_official.sh
```

会自动选择 `python3.12` 或 `python3.11`，不会强行覆盖系统 Python。

---

## 6. 手动安装依赖

```bash
pip install -r requirements.txt
```

如果默认 `python` 不是 3.11 / 3.12：

```bash
python3.11 -m pip install -r requirements.txt
# 或
python3.12 -m pip install -r requirements.txt
```

---

## 7. API 配置

支持两种方式：

```text
1. 中转站 API 配置（推荐）
2. 官方 API 配置
```

### 7.1 中转站配置

复制 `.env.proxy.example` 为 `.env`，填写：

```env
OPENAI_API_KEY=your_openai_proxy_api_key_here
OPENAI_API_BASE=https://4router.net/v1
ANTHROPIC_API_KEY=your_anthropic_proxy_api_key_here
ANTHROPIC_BASE_URL=https://4Router.net

MODEL_ANALYSIS=gpt-5.5
MODEL_DATA_PROCESS=claude-opus-4-6
MODEL_CODER_API=gpt-5.4-mini
MODEL_MANAGER_SUMMARY=gpt-5.4-mini

CODER_EXECUTION_MODE=API
```

中转站默认模型分配：

| Agent             | 模型                | API 来源                   |
| ----------------- | ----------------- | ------------------------ |
| analysis_agent    | `gpt-5.5`         | `https://4router.net/v1` |
| data_processing_agent | `claude-opus-4-6` | `https://4Router.net`    |
| manager_agent     | `gpt-5.4-mini`    | `https://4router.net/v1` |
| summary_agent     | `gpt-5.4-mini`    | `https://4router.net/v1` |
| reproduction_agent| `MODEL_CODER_API` | API / 本地 CLI 工具 |

### 7.2 官方 API 配置

复制 `.env.example` 为 `.env`，填写：

```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

---

## 8. Skills 自定义

每个 Agent 都拥有一个独立的 skills 目录，目录里所有 `.md` 文件会按文件名升序自动拼接进对应 Agent 的 backstory。

例如：

```text
skills/data_processing_agent/
├── 01_base_rules.md
├── 02_data_cleaning_rules.md
├── 03_missing_value_rules.md
├── 04_exception_rules.md
└── 05_output_rules.md
```

修改这些文件后**不需要改 Python 代码**，下一次跑 `analysis.py` / `main.py` 就会立即生效。

写规则时建议遵循：

```text
1. 一条规则一行
2. 用祈使语气：必须 / 禁止 / 应当
3. 文件命名前面加 01_ / 02_ 保证读取顺序稳定
4. 同类规则放进同一个 .md，避免规则散落
```

---

## 9. Agent 留痕日志

每个 Agent 都会把行为写到独立的 Markdown 日志，方便事后审计：

```text
logs/agents/analysis_agent.md
logs/agents/data_processing_agent.md
logs/agents/manager_agent.md
logs/agents/reproduction_agent.md
logs/agents/summary_agent.md
```

每个日志中会记录：

```text
- Agent 启动 / 结束事件
- 每个 Task 的开始时间、描述
- 每个 Task 的完整输出（必要时截断）
- 每次工具调用的入参 / 出参
- 异常堆栈
```

阶段一只重置 `analysis_agent.md`；阶段二会重置后 4 个 Agent 的日志。  
留痕模块出现兼容性问题时会**自动降级为 no-op**，不会阻断主流程。

---

## 10. 外部代码工具链：Codex CLI / Claude Code

如果希望复现 Agent 走本地 CLI，编辑 `.env`：

```env
CODER_EXECUTION_MODE=CLI_CODEX     # 使用本地 codex
# 或
CODER_EXECUTION_MODE=CLI_CLAUDE    # 使用本地 claude code
```

CLI 模式下，`reproduction_agent` 仍使用 `MODEL_CODER_API` 对应的 LLM 进行任务规划与 prompt 组织；Codex CLI / Claude Code CLI 只作为工具被 Agent 调用，不会被当成模型名传给 LLM。

并确保终端里能直接执行：

```bash
codex --version
# 或
claude --version
```

否则请回退到：

```env
CODER_EXECUTION_MODE=API
```

---

## 11. 完整运行步骤

### Step 1：下载项目

```bash
git clone <your-repo-url>
cd recurrence_report_agent
```

### Step 2：安装依赖

Windows：

```bat
setup_windows_global.bat
```

Mac / Linux：

```bash
chmod +x setup_mac_linux_official.sh
./setup_mac_linux_official.sh
```

或手动：

```bash
pip install -r requirements.txt
```

### Step 3：配置 API

```text
中转站：复制 .env.proxy.example → .env，填写 OPENAI_API_KEY / ANTHROPIC_API_KEY
官方：  复制 .env.example       → .env，填写 OPENAI_API_KEY 和 ANTHROPIC_API_KEY
```

### Step 4：放入研报

```text
Report/alpha_strategy_report.pdf
```

### Step 5：运行阶段一

```bash
python analysis.py
```

运行结束后查看：

```text
outputs/summary.md
outputs/data_requirements.md
logs/agents/analysis_agent.md
```

### Step 6：根据数据需求放入原始数据

```text
raw_data/market_data.csv
raw_data/factor_data.xlsx
raw_data/benchmark_data.csv
```

### Step 7：运行阶段二

```bash
python main.py
```

如果默认 `python` 版本不合规，可以使用 `python3.11` / `python3.12` 替代。

### Step 8：查看最终输出

```text
outputs/data_clean.py
outputs/data_overview.md
outputs/backtest.py
outputs/final_report.md
logs/agents/*.md
```

---

## 12. 预期输出样例

### `summary.md`

```markdown
# 研报核心摘要：《基于XX因子的自适应动量策略》

- 核心逻辑：利用波动率调整传统动量因子。
- 回测周期建议：2018年1月 - 2026年6月。
- 策略类型：横截面因子选股 / 时间序列择时 / 多资产配置。
```

### `data_requirements.md`

```markdown
# 数据需求清单

| 字段名称 | 类型 | 频次 | 备注 |
|---|---|---|---|
| close_price | float | 日频 | 标的收盘价，需复权 |
| volume | int | 日频 | 成交量 |
| benchmark_return | float | 日频 | 基准指数收益率 |
```

### `data_clean.py`

```python
import pandas as pd
import numpy as np

def clean_market_data(df):
    try:
        # 统一日期格式
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

        # 缺失值处理
        df = df.ffill()

        # 异常值处理
        q = df["close_price"].quantile([0.01, 0.99])
        df["close_price"] = np.clip(df["close_price"], q.iloc[0], q.iloc[1])

        return df
    except Exception as e:
        print(f"清洗出错: {e}")
        raise
```

### `final_report.md`

```markdown
# 项目全流程复现总结报告

## 1. 策略背景
本策略来源于用户上传的研究报告，核心思想是基于价格动量、风险调整和交易成本控制构建交易信号。

## 2. 自动化执行链路
- 分析阶段：完成研报解析和数据需求提取
- 数据阶段：完成原始数据读取和清洗代码生成
- 回测阶段：完成策略复现代码生成
- 审查阶段：完成代码逻辑检查
- 总结阶段：输出最终复现报告

## 3. 输出文件
- outputs/summary.md / outputs/data_requirements.md
- outputs/data_clean.py / outputs/data_overview.md
- outputs/backtest.py / outputs/final_report.md
- logs/agents/*.md

## 4. 风险提示
本项目生成的结果仅用于研究报告复现和学习，不构成任何投资建议。
```

---

## 13. 常见问题

### Q1：为什么要先运行 `analysis.py`，再运行 `main.py`？

阶段二会做前置校验：

```text
require_phase1_outputs()  # 检查 outputs/summary.md / outputs/data_requirements.md 是否存在
require_raw_data()        # 检查 raw_data/ 是否非空
```

任何一个缺失都会直接 `sys.exit`。所以必须先跑阶段一并准备好原始数据。

### Q2：为什么 `main.py` 报错说找不到原始数据？

请确认：

```text
raw_data/  存在且不为空
```

### Q3：研报应该放在哪里？

```text
Report/
```

PDF / Word 都可以，会被分析 Agent 自动扫描。

### Q4：为什么找不到 `agents.yaml` 或 `tasks.yaml`？

它们必须位于：

```text
config/agents.yaml
config/tasks.yaml
```

### Q5：为什么 Codex CLI 不能运行？

请确保终端里能直接执行：

```bash
codex --version
```

否则请改用：

```env
CODER_EXECUTION_MODE=API
```

### Q6：可以不用 Codex CLI 吗？

完全可以。设置 `CODER_EXECUTION_MODE=API`，复现 Agent 就会直接使用 LLM 生成 `backtest.py`。

### Q7：Agent 留痕日志会不会越写越大？

每次跑阶段一 / 阶段二启动时，对应阶段的日志文件会被清空重置，再追加新内容。所以日志只保留最近一次运行。

### Q8：怎么修改 Agent 行为？

最推荐的方式是改 `skills/<agent_name>/*.md`，不要去改 `agents.py`。  
`config/agents.yaml` 是基础角色设定，`skills/` 是规则补丁，分工明确。

---

## 14. 项目声明

本项目用于研究报告复现、自动化投研流程学习与量化回测代码生成实验。

本项目输出结果不构成任何投资建议，不保证策略有效性、收益稳定性或数据准确性。用户应自行检查数据质量、代码逻辑和回测假设。
