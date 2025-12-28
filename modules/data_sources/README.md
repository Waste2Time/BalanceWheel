# 数据源模块（data_sources）

## 已完成
- 统一接口 `IDataSource.fetch(symbol, start, end, frequency) -> DataSet`，可注入 fetcher 以避免硬依赖。
- 数据模型 `Bar`/`DataSet`，支持排序、切片并用于后续回测。
- CSV 读写工具 `save_csv`/`load_csv` 与缓存元数据写入 `CacheMetadata`。
- 基础交叉验证 `validate_pair`：缺失比例、收盘价均值/极值差异统计，并可落地 JSON。
- 提供离线可用的随机漫步示例 fetcher（`random_walk_fetcher`）。

## 必须完成但未完成
- 真实的 baostock 与 akshare fetcher 适配（含字段映射与复权处理）。
- CSV 缓存增量更新策略与多版本管理。
- 更完整的交叉验证报告（价量偏差、复权因子、缺口填补日志）。

## 可选项
- 扩展至 tushare/聚宽/期货/外汇等数据源适配器。
- 本地数据质量评分与异常检测（闪崩、极值过滤）。
- 数据缓存目录结构自动管理与多版本切换工具。
