# 实验对比模块（experiment_runner）

## 目标

- 支持 baseline 与 variant 的批量回测对比。
- 保证实验可重复、可追溯。

## 功能

- 统一配置：数据区间、回测参数、手续费等。
- 批量执行：多策略并行或顺序执行。
- 结果聚合：指标对比表、胜率统计。

## 输出

- 对比指标表（收益、最大回撤、Sharpe）
- 对比曲线图（收益曲线、回撤曲线）
- 实验元数据（配置、数据版本、运行时间）

## 记录与复现

- 建议在 `experiments/` 下保存 run metadata。
- 记录使用的数据文件 hash 或版本号。

## 与其他模块衔接

- 调用 BacktestEngineAdapter 运行回测。
- 输出交由 ReportingUI 生成图表。
