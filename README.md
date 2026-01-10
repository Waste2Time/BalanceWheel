# BalanceWheel

BalanceWheel 是一个面向个人使用、低成本、可迭代的量化策略回测框架。项目遵循“小步快跑”的原则，当前仅完成数据层的最小可用能力。

## 架构概览

- **数据层 (`balancewheel/data`)**：提供统一接口适配数据源，并对 OHLCV 数据进行标准化与落地保存。
- **回测引擎层 (`balancewheel/engine`)**：负责撮合、资金曲线与订单管理（待建设）。
- **策略层 (`balancewheel/strategy`)**：封装策略逻辑与信号生成（待建设）。
- **评估与报告层 (`balancewheel/report`)**：负责绩效分析与报告输出（待建设）。

统一入口位于 `main.py`，用于串联未来完整链路。

## 当前可用功能

- 数据层提供 Akshare 与 Baostock 的日线 OHLCV 拉取接口。
- 统一 Schema：`datetime, open, high, low, close, volume, amount`。
- 数据落地保存为 CSV。
- 数据校验与多源交叉验证，并记录元信息到 `data/_meta`。

## 本地检查

```bash
python -m balancewheel.data
```
