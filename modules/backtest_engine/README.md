# 回测引擎适配模块（backtest_engine）

## 已完成
- 定义 `IBacktestEngine` 接口与统一结果结构（权益曲线、交易记录、日收益序列、绩效指标）。
- 提供轻量 `SimpleBacktestEngine`，支持初始资金、手续费，并计算 Sharpe/Sortino/Calmar、波动率、年化收益、胜率等指标。
- 新增多标的轮动引擎 `RotationBacktestEngine` + `RotationConfig`，用于单账户在多标的间切换持仓的策略验证。
- 接入 vn.py CTA 回测引擎，提供委托策略包装器，将自定义 `Strategy` 映射到 vn.py 的 `CtaTemplate` 并复用统一指标计算。
- 新增 `__main__` 入口，支持 `python -m modules.backtest_engine` 获取模块用法提示。

## 必须完成但未完成
- 支持滑点、复合费用、保证金/合约乘数、分红送股处理。
- 更严谨的多标的撮合（不同交易日历/缺失数据处理）与组合级别持仓管理。
- 更全面的风险指标（VaR/ES）、超额收益对数收益的统计检验。

## 可选项
- 并行回测与向量化加速。
- 回测日志、事件回放与可交互调试。
- 与实盘风控/风控联动的仿真撮合。 
