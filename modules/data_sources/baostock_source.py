from __future__ import annotations

from datetime import datetime
import importlib.util

from .base import IDataSource
from .models import Bar, DataSet

DATE_FORMAT = "%Y-%m-%d"


class BaostockSource(IDataSource):
    """Baostock 适配器，直接调用 baostock SDK 拉取日线数据。"""

    def __init__(self, adjust_flag: str = "3") -> None:
        """
        :param adjust_flag: 复权方式，baostock 默认 3 为不复权，可根据需求传入 1/2 进行前/后复权。
        """

        self.adjust_flag = adjust_flag

    def _require_dependency(self) -> None:
        if importlib.util.find_spec("baostock") is None:
            raise ImportError("baostock 未安装，请执行 `pip install baostock`。")

    def _map_frequency(self, frequency: str) -> str:
        if frequency != "1d":
            raise ValueError("BaostockSource 目前仅支持日线频率 '1d'")
        return "d"

    def fetch(self, symbol: str, start: datetime, end: datetime, frequency: str) -> DataSet:
        self._require_dependency()
        import baostock as bs

        interval = self._map_frequency(frequency)
        start_str = start.strftime(DATE_FORMAT)
        end_str = end.strftime(DATE_FORMAT)

        login_result = bs.login()
        if login_result.error_code != "0":
            raise RuntimeError(f"baostock 登录失败: {login_result.error_msg}")

        try:
            fields = "date,open,high,low,close,volume"
            query = bs.query_history_k_data_plus(
                code=symbol,
                fields=fields,
                start_date=start_str,
                end_date=end_str,
                frequency=interval,
                adjustflag=self.adjust_flag,
            )
            if query.error_code != "0":
                raise RuntimeError(f"baostock 查询失败: {query.error_msg}")

            bars: list[Bar] = []
            while query.error_code == "0" and query.next():
                row = query.get_row_data()
                bars.append(
                    Bar(
                        symbol=symbol,
                        datetime=datetime.strptime(row[0], DATE_FORMAT),
                        open=float(row[1]),
                        high=float(row[2]),
                        low=float(row[3]),
                        close=float(row[4]),
                        volume=float(row[5]),
                    )
                )
        finally:
            bs.logout()

        return DataSet.from_iterable(symbol=symbol, frequency=frequency, bars=bars)
