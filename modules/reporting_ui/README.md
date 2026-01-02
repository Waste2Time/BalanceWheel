# 报告与 UI 模块（reporting_ui）

## 已完成
- 构建报告函数 `build_report`：生成权益曲线图（matplotlib 优先，缺省回落 CSV）并输出指标文本文件。
- 批量报告 `build_experiment_reports`：生成多策略权益叠加图、指标表 CSV、显著性检验结果文件，并回填到策略级报告。
- 新增 `__main__` 入口，支持 `python -m modules.reporting_ui` 查看用法提示。

## 必须完成但未完成
- 交互式图表（plotly/bokeh）与网页化报告导出。
- 更丰富的表格排版（Markdown/HTML）与指标高亮规则。
- 与 ExperimentRunner 的统一目录版本化与配置注入。

## 可选项
- Web UI 或 vn.py UI 的集成入口。
- 图表主题/样式配置与多语言支持。
- 自动生成 markdown/PDF 报告。
