# 报告与 UI 模块（reporting_ui）

## 已完成
- 生成收益曲线与回撤曲线图（matplotlib 输出 PNG）。
- 报告打包 `ReportBundle`，封装图表路径与指标文本（metrics.txt）。

## 必须完成但未完成
- 指标表的格式化与多策略对比图输出。
- 报告落地结构（reports/<experiment_id>/）与实验 runner 对接（聚合多策略）。
- 与 vn.py UI/其他前端的适配层。

## 可选项
- 交互式图表（plotly/bokeh）与静态导出并存。
- 报告模板（Markdown/PDF/HTML）自动生成。
- 图表主题与品牌定制。
