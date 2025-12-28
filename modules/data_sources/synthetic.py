from __future__ import annotations

import random
from datetime import datetime, timedelta

from .base import IDataSource
from .models import Bar, DataSet


class SyntheticSource(IDataSource):
    """离线随机游走数据源，便于快速跑通流程。"""

    def __init__(self, seed: int | None = 42, start_price: float = 100.0) -> None:
        self._rng = random.Random(seed)
        self._start_price = start_price

    def fetch(self, symbol: str, start: datetime, end: datetime, frequency: str) -> DataSet:
        if frequency != "1d":
            raise ValueError(f"SyntheticSource 目前仅支持日线 frequency='1d'，收到: {frequency}")

        if start > end:
            raise ValueError("start 时间必须早于 end 时间")

        bars: list[Bar] = []
        price = self._start_price
        current = start
        while current <= end:
            drift = self._rng.gauss(0, 0.02)
            price = max(price * (1 + drift), 0.1)
            high = price * (1 + abs(self._rng.gauss(0, 0.005)))
            low = price * (1 - abs(self._rng.gauss(0, 0.005)))
            close = price
            open_price = (high + low) / 2
            volume = abs(self._rng.gauss(1_000_000, 250_000))
            bars.append(
                Bar(
                    symbol=symbol,
                    datetime=current,
                    open=open_price,
                    high=max(high, low),
                    low=min(high, low),
                    close=close,
                    volume=volume,
                )
            )
            current += timedelta(days=1)

        return DataSet.from_iterable(symbol=symbol, frequency=frequency, bars=bars)
