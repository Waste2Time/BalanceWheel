# 报告与 UI 模块（reporting_ui）

## 目标

- 回测结束生成图片（收益曲线、回撤曲线、对比图）。
- 可选择 vn.py UI 或轻量图表工具。

## 输出类型

- 收益曲线（equity curve）
- 回撤曲线（drawdown）
- 月度/年度收益表
- 多策略对比图

## UI 方案

- **方案 A**：调用 vn.py 内置图表/GUI。
- **方案 B**：matplotlib/plotly 输出 PNG。

## 与 ExperimentRunner 的对接

- 接收统一回测结果与指标。
- 批量生成图片与报告。

## 建议目录

- `reports/<experiment_id>/` 下存放图片与对比结果。
