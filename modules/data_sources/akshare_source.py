from __future__ import annotations

from datetime import datetime
from typing import Callable, Iterable

from .base import IDataSource
from .models import Bar, DataSet

FetchCallable = Callable[[str, datetime, datetime, str], Iterable[Bar]]


class AkshareSource(IDataSource):
    """Akshare 适配器（通过注入 fetcher 以避免硬依赖）。"""

    def __init__(self, fetcher: FetchCallable | None = None) -> None:
        self._fetcher = fetcher

    def fetch(self, symbol: str, start: datetime, end: datetime, frequency: str) -> DataSet:
        if self._fetcher is None:
            raise NotImplementedError("Akshare fetcher 未注入。")
        bars = self._fetcher(symbol, start, end, frequency)
        return DataSet.from_iterable(symbol=symbol, frequency=frequency, bars=bars)
