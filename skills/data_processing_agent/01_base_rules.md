# 数据处理 Agent 基础规则

1. 只处理 raw_data/ 中实际存在的数据。
2. 禁止编造不存在的数据字段。
3. 禁止修改 raw_data/ 中的原始文件。
4. 所有处理结果必须输出到 outputs/ 或 processed_data/。
