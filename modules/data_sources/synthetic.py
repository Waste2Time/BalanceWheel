from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Iterable

from .models import Bar


def random_walk_fetcher(seed: int = 42, start_price: float = 100.0, volatility: float = 0.01, step: timedelta | None = None):
    step = step or timedelta(days=1)

    def _fetch(symbol: str, start: datetime, end: datetime, frequency: str) -> Iterable[Bar]:
        rng = random.Random(seed)
        current = start_price
        current_time = start
        while current_time <= end:
            change = rng.uniform(-volatility, volatility)
            open_price = current
            close_price = max(0.01, current * (1 + change))
            high = max(open_price, close_price) * (1 + rng.uniform(0, volatility / 2))
            low = min(open_price, close_price) * (1 - rng.uniform(0, volatility / 2))
            volume = abs(change) * 1_000_000
            yield Bar(
                symbol=symbol,
                datetime=current_time,
                open=open_price,
                high=high,
                low=low,
                close=close_price,
                volume=volume,
            )
            current = close_price
            current_time += step

    return _fetch
