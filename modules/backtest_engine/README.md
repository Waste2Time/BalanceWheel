# 回测引擎适配模块（backtest_engine）

## 已完成
- 统一接口 `IBacktestEngine.run(strategy, data, config) -> BacktestResult`。
- 轻量单标的引擎 `SimpleBacktestEngine`：支持初始资金、手续费、仓位裁剪（`PositionSizer`）。
- 结果模型 `BacktestResult`/`EquityPoint`/`Trade`，可计算总收益、年化收益、波动率、Sharpe、最大回撤，并支持回撤风控钩子。

## 必须完成但未完成
- vn.py 适配器的真实实现（数据加载、参数映射、结果转换）。
- 多标的/组合回测支持（含滑点、成交量约束、逐笔撮合）。
- 更丰富的绩效指标（Calmar 等）与可插拔风险管理。

## 可选项
- 并行回测与向量化引擎以提升性能。
- 事件驱动日志/调试钩子，便于 trouble shooting。
- 与外部分析工具（如 pandas/pyfolio）的适配层。
