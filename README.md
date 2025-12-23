Balance Wheel

## 框架总览

面向个人、低成本量化策略回测平台的目标是：以可插拔的数据源与回测引擎为核心，支持单标的、轮动与组合策略，多策略对比与可视化输出，并确保可复现实验与排错（trouble shooting）。

### 模块总览（逻辑图）

```mermaid
flowchart TD
    A[DataSourceAdapter<br/>数据源适配] --> B[DataValidation<br/>交叉验证/清洗]
    B --> C[CSVCache<br/>本地CSV缓存]
    C --> D[UnifiedDataModel<br/>统一数据模型]
    D --> E[BacktestEngineAdapter<br/>回测引擎适配]
    E --> F[StrategyLibrary<br/>策略库]
    F --> G[PortfolioRisk<br/>组合与风控]
    E --> H[ExperimentRunner<br/>多策略对比/实验]
    H --> I[ReportingUI<br/>图表/报告/UI输出]

    subgraph DataSourceAdapter
        A1[Baostock]
        A2[AkShare]
    end

    subgraph BacktestEngineAdapter
        E1[vn.py]
        E2[其他引擎(预留)]
    end
```

### 数据与流程

1. 数据拉取：通过 DataSourceAdapter 抽象接口接入数据源（初期 baostock + akshare），对同一标的、区间进行交叉验证。
2. 数据缓存：清洗后落地为 CSV，以路径与命名规范管理版本（便于可复现）。
3. 回测执行：统一数据模型进入 BacktestEngineAdapter（默认 vn.py），注入策略与风控组件。
4. 实验对比：ExperimentRunner 以 baseline + variant 方式批量执行，输出对比指标。
5. 可视化输出：ReportingUI 生成收益曲线、回撤曲线、对比图等图片。

### 目录结构建议

```
modules/
  data_sources/         # 数据源适配、交叉验证、CSV缓存
  backtest_engine/      # vn.py 适配与统一回测接口
  strategies/           # 单标的/轮动/组合策略
  portfolio_risk/       # 风控与组合管理
  experiment_runner/    # 多策略对比与实验管理
  reporting_ui/         # 图表与UI输出
  pipeline/             # 串联与端到端流程
```

### 最低可行版本（MVP）

1. 数据源适配：baostock + akshare 交叉验证并落地 CSV。
2. 回测引擎：vn.py 接入，统一回测接口。
3. 策略示例：单标的（如均线交叉）与轮动策略。
4. 多策略对比：baseline + variant 批量回测。
5. 图表输出：回测结束生成收益曲线/回撤图（PNG）。
