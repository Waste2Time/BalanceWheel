from __future__ import annotations

from datetime import datetime
import importlib.util
from typing import Iterable

from .base import IDataSource
from .models import Bar, DataSet

DATE_FORMAT = "%Y%m%d"


class AkshareSource(IDataSource):
    """Akshare 适配器，直接调用 akshare 提供的日线行情接口。"""

    def _require_dependency(self) -> None:
        if importlib.util.find_spec("akshare") is None:
            raise ImportError("akshare 未安装，请执行 `pip install akshare`。")

        if importlib.util.find_spec("pandas") is None:
            raise ImportError("pandas 未安装，akshare 数据转换需要 `pip install pandas`。")

    def _map_frequency(self, frequency: str) -> str:
        if frequency != "1d":
            raise ValueError("AkshareSource 目前仅支持日线频率 '1d'")
        return "daily"

    def _parse_bars(self, df, symbol: str, frequency: str) -> Iterable[Bar]:
        columns = {
            "date": "日期",
            "open": "开盘",
            "high": "最高",
            "low": "最低",
            "close": "收盘",
            "volume": "成交量",
        }
        # 兼容英文字段命名
        fallback = {
            "date": "date",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume",
        }
        bars: list[Bar] = []
        for _, row in df.iterrows():
            get = lambda key: row[columns.get(key, fallback[key])]
            bars.append(
                Bar(
                    symbol=symbol,
                    datetime=datetime.strptime(str(get("date")), "%Y-%m-%d"),
                    open=float(get("open")),
                    high=float(get("high")),
                    low=float(get("low")),
                    close=float(get("close")),
                    volume=float(get("volume")),
                )
            )
        return bars

    def fetch(self, symbol: str, start: datetime, end: datetime, frequency: str) -> DataSet:
        self._require_dependency()
        import akshare as ak

        period = self._map_frequency(frequency)
        start_str = start.strftime(DATE_FORMAT)
        end_str = end.strftime(DATE_FORMAT)

        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period=period,
            start_date=start_str,
            end_date=end_str,
            adjust="qfq",
        )
        bars = self._parse_bars(df, symbol, frequency)
        return DataSet.from_iterable(symbol=symbol, frequency=frequency, bars=bars)
