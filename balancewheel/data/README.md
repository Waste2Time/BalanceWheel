# 数据层

## 已完成能力

- 统一数据接口 `DataProvider`，适配 Akshare 与 Baostock。
- 日线 OHLCV 数据规范化为统一 Schema。
- CSV 落地保存。

## 暴露接口

- `DataRequest`：描述数据请求（标的、资产类型、日期范围）。
- `DataProvider.fetch_daily_ohlcv`：拉取日线 OHLCV 原始数据。
- `DataService.fetch_and_save`：拉取、规范化并保存数据。
- `CsvRepository.save`：保存 CSV。

## 使用示例

```python
from balancewheel.data import DataRequest, CsvRepository, DataService
from balancewheel.data.providers import AkshareProvider, BaostockProvider

service = DataService(
    providers={
        "akshare": AkshareProvider(),
        "baostock": BaostockProvider(),
    },
    repository=CsvRepository("data"),
)

request = DataRequest(symbol="000001", asset_type="stock", start="20240101", end="20240131")
service.fetch_and_save(request, provider_name="akshare")
```

## 测试命令

```bash
python -m balancewheel.data
```
