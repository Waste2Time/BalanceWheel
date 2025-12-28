# 回测引擎适配模块（backtest_engine）

## 目标

- 提供统一的回测引擎接口，默认适配 vn.py。
- 在不修改策略逻辑的情况下可切换回测引擎。

## 接口设计

```
class IBacktestEngine:
    def run(self, strategy, data, config) -> BacktestResult:
        """执行回测并返回统一结果结构"""
```

### 统一结果结构

建议包含：

- `equity_curve`（时间序列）
- `performance_metrics`（年化、最大回撤、Sharpe 等）
- `trades`（交易明细）
- `positions`（仓位变化）

## vn.py 适配细节

- 初始化回测引擎（回测起止时间、频率、基准）。
- 数据加载：读取统一数据模型或 CSV。
- 回测配置：手续费、滑点、保证金、合约乘数。
- 输出转换：将 vn.py 结果映射为统一结构。

## 多策略对比衔接

- 通过 ExperimentRunner 批量调用 `run()`。
- 保证相同数据与配置下可复现对比。

## 扩展点

- 支持其他引擎（Backtrader、zipline 等）。
- 提供回测日志与调试钩子。
