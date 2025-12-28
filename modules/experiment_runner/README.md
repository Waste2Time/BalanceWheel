# 实验对比模块（experiment_runner）

## 已完成
- 实验配置 `ExperimentConfig`（名称、标的、时间区间、频率、回测引擎配置、输出目录）。
- `ExperimentRunner` 批量执行多个策略并返回 `ExperimentResult`，包含指标汇总表，并可落地 `metadata.json` 与 `summary.json`。

## 必须完成但未完成
- 更丰富的指标对齐/排序展示（总收益、回撤、Sharpe 等）并支持多实验聚合。
- 并行/异步调度以加速多策略对比。
- 运行元数据版本化（数据版本、代码提交信息等）。

## 可选项
- 试验配置模板化（YAML/JSON + 变量覆盖）。
- 实验排行榜/可视化对比页面。
- 自动化超参搜索或贝叶斯优化入口。
