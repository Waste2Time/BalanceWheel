# 报告与 UI 模块（reporting_ui）

## 已完成
- 构建基础报告函数 `build_report`：生成权益曲线图（有 matplotlib 备用文本导出）并输出基础指标文本文件。
- 新增 `__main__` 入口，支持 `python -m modules.reporting_ui` 查看用法提示。

## 必须完成但未完成
- 报表指标汇总（收益、回撤、夏普等）与表格输出。
- 多策略对比图（叠加/分组）与交互式图表选项。
- 与 ExperimentRunner 的统一报告入口与目录管理。

## 可选项
- Web UI 或 vn.py UI 的集成入口。
- 图表主题/样式配置与多语言支持。
- 自动生成 markdown/PDF 报告。
