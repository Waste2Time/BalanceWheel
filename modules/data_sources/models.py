from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


@dataclass(frozen=True)
class Bar:
    symbol: str
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class DataSet:
    symbol: str
    frequency: str
    bars: tuple[Bar, ...]

    @classmethod
    def from_iterable(cls, symbol: str, frequency: str, bars: Iterable[Bar]) -> "DataSet":
        return cls(symbol=symbol, frequency=frequency, bars=tuple(bars))
