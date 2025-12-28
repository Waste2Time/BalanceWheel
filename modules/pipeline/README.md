# 流程编排模块（pipeline）

## 目标

- 串联数据源、回测引擎、策略、风控、对比与报告。
- 提供端到端的运行入口。

## 入口设计

- CLI 或配置驱动（YAML/JSON）。
- 统一传入标的池、时间区间与回测参数。

## 端到端流程伪代码

```
config = load_config("config.yml")
raw_data = data_source.fetch(config.symbol, config.start, config.end)
clean = validate_and_cache(raw_data)
result = backtest_engine.run(strategy, clean, config)
reporting.render(result)
```

## 最小可行示例

- 单标的策略 + 结果图输出。
- 基线与改动策略对比输出。

## 扩展方向

- 插件式新增数据源与引擎。
- 多市场/多资产统一回测接口。
