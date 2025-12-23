# 策略库模块（strategies）

## 目标

- 支持单标的、轮动与组合策略。
- 以可配置参数驱动策略，支持 baseline 与 variant 对比。

## 策略模板

- `SingleAssetStrategy`：单标的策略模板。
- `RotationStrategy`：轮动策略（资产池 + 信号排序）。
- `PortfolioStrategy`：组合策略（多资产权重与再平衡）。

## 信号与执行解耦

- `signal_generator`：生成买卖信号。
- `position_sizer`：根据风控与资金分配仓位。
- `execution`：将信号转换为交易指令。

## Baseline 与 Variant

- 基线策略：固定参数/规则（如均线交叉）。
- 改动策略：在 baseline 上修改参数或信号逻辑。
- ExperimentRunner 中同数据对比。

## 示例策略

- 均线交叉（单标的）
- 动量轮动（ETF/行业）
- 波动率约束组合（多资产）

## 关键配置

- `lookback_window`
- `rebalance_frequency`
- `universe`（标的池）
- `risk_budget`
