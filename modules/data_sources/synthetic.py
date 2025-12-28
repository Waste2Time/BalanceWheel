from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd

from .base import DataSource, ensure_ohlcv_columns


class SyntheticSource(DataSource):
    """Generate random-walk OHLCV data for offline experimentation."""

    def __init__(self, seed: Optional[int] = None, start_price: float = 100.0):
        self.seed = seed
        self.start_price = start_price

    def fetch(
        self, symbol: str, start: Optional[date] = None, end: Optional[date] = None
    ) -> pd.DataFrame:
        rng = np.random.default_rng(self.seed)
        start_dt = datetime.combine(start or date(2020, 1, 1), datetime.min.time())
        end_dt = datetime.combine(end or date.today(), datetime.min.time())
        days = (end_dt - start_dt).days + 1
        dates = [start_dt + timedelta(days=i) for i in range(days)]
        returns = rng.normal(loc=0.0005, scale=0.01, size=days)
        prices = [self.start_price]
        for r in returns[1:]:
            prices.append(prices[-1] * (1 + r))
        prices = np.array(prices)
        highs = prices * (1 + rng.normal(0.002, 0.002, size=days))
        lows = prices * (1 - rng.normal(0.002, 0.002, size=days))
        volumes = rng.integers(low=1_000, high=10_000, size=days)
        df = pd.DataFrame(
            {
                "open": prices,
                "high": highs,
                "low": lows,
                "close": prices,
                "volume": volumes,
            },
            index=pd.to_datetime(dates),
        )
        df.index.name = "date"
        return ensure_ohlcv_columns(df)
