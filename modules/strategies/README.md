# 策略库模块（strategies）

## 已完成
- 基础抽象 `Strategy`，统一 `on_bar(bar, history) -> target_position` 接口。
- 单标的均线交叉策略 `MovingAverageCrossStrategy`，参数化短/长均线窗口与仓位。
- 轮动信号生成器 `RotationStrategy`，按动量得分排序并截取 Top K。
- 组合权重模板 `PortfolioStrategy`，支持权重归一化。

## 必须完成但未完成
- 与风控/仓位模块的对接（position sizing、风险钩子）。
- 更丰富的策略样例（突破、均值回归、波动率控制的组合策略）。
- 参数扫描/网格搜索支持，便于 baseline 与 variant 对比。

## 可选项
- 策略元数据与日志埋点，辅助调试与可视化。
- 事件驱动的交易执行抽象（信号 -> 订单 -> 成交）。
- 策略回放/模拟实时接口（用于 paper trading）。
