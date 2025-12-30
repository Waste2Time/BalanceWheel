# 回测引擎适配模块（backtest_engine）

## 已完成
- 定义 `IBacktestEngine` 接口与统一结果结构（权益曲线、交易记录、基础指标）。
- 提供轻量 `SimpleBacktestEngine`，支持初始资金与手续费参数。
- 计算基本绩效指标：总收益率与最大回撤。
- 接入 vn.py CTA 回测引擎，提供委托策略包装器，将自定义 `Strategy` 映射到 vn.py 的 `CtaTemplate`。
- 新增 `__main__` 入口，支持 `python -m modules.backtest_engine` 获取模块用法提示。

## 必须完成但未完成
- 支持滑点、复合费用、保证金/合约乘数、分红送股处理。
- 多标的与组合级别的回测（含同步撮合与持仓管理）。
- 统一导出更丰富的统计指标（如 Sharpe、Sortino、Calmar 等）。

## 可选项
- 并行回测与向量化加速。
- 更丰富的风险指标与归因分析。
- 回测日志、事件回放与可交互调试。
