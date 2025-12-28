# 数据源模块（data_sources）

## 目标

- 以统一接口接入多数据源（初期 baostock + akshare）。
- 对同一标的、同一时间区间进行交叉验证，提升数据可信度。
- 清洗后的数据落地为 CSV，支持可复现与增量更新。

## 接口设计

建议定义统一数据源接口：

```
class IDataSource:
    def fetch(self, symbol: str, start: datetime, end: datetime, frequency: str) -> DataSet:
        """返回统一字段的行情数据"""
```

### 统一字段规范

建议字段：

- `datetime`（ISO8601 或时间戳）
- `open`, `high`, `low`, `close`, `volume`

## 数据清洗与校验

1. **字段对齐**：强制标准字段，保留原始字段映射表。
2. **缺失处理**：缺失行删除或前向填充（视策略要求）。
3. **去重与排序**：按时间排序、移除重复时间戳。
4. **交叉验证**：同窗口的 `close` 差异统计。

## CSV 落地策略

- 路径规范：`data/<source>/<symbol>/<frequency>.csv`
- 命名规范：`YYYYMMDD_YYYYMMDD.csv`（可选）
- 增量更新：按最后时间戳进行追加写入
- 版本记录：记录数据源版本与更新时间戳（metadata 文件或 header）

## 交叉验证流程

1. 分别从 baostock 与 akshare 拉取同一标的同一时间区间。
2. 规范化字段与时间索引。
3. 计算差异指标（绝对差、相对差、缺失比例）。
4. 将验证结果保存为 `validation_report.json` 或 CSV。

## 扩展点

- 预留 tushare、聚宽等数据源适配器。
- 支持期货、外汇、ETF、贵金属等标的类别。

## 示例伪代码

```
source = BaostockSource(fetcher=...)
raw = source.fetch("600000.SH", start, end, "1d")
write_csv("data/baostock/600000.SH/1d.csv", raw)
```
