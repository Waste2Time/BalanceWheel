# 实验对比模块（experiment_runner）

## 已完成
- `ExperimentConfig` 与 `ExperimentRunner`，可批量执行多策略并收集结果。
- 聚合性能指标表（收益、回撤、Sharpe、Sortino、Calmar、波动率、胜率等）。
- 统计显著性：提供基于日收益的 Welch t 检验与均值对比，输出 CSV 汇总。
- 新增 `__main__` 入口，支持 `python -m modules.experiment_runner` 输出用法提示。

## 必须完成但未完成
- 统一实验结果持久化（元数据、数据版本、指标快照）。
- 并行/异步调度与进度跟踪。
- 更丰富的假设检验（如非参数检验、效应量计算）与置信区间输出。

## 可选项
- CLI/配置驱动的实验批处理。
- 与报告模块联动生成多策略对比图与汇总表。
- 统一日志体系与错误重试。
