# Codex CLI 使用规则

1. 如果使用 Codex CLI，复现 Agent 不应该直接在 CrewAI 输出中写完整代码。
2. 复现 Agent 应构造清晰 prompt，并调用 Codex CLI 生成 backtest.py。
3. Codex CLI 生成的代码必须落盘到指定路径。
4. CrewAI 的任务输出应记录 Codex CLI 调用日志，而不是覆盖 backtest.py。
