from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Sequence


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
        ordered = sorted(bars, key=lambda bar: bar.datetime)
        return cls(symbol=symbol, frequency=frequency, bars=tuple(ordered))

    def slice(self, start: datetime | None = None, end: datetime | None = None) -> "DataSet":
        filtered: Sequence[Bar] = self.bars
        if start is not None:
            filtered = [bar for bar in filtered if bar.datetime >= start]
        if end is not None:
            filtered = [bar for bar in filtered if bar.datetime <= end]
        return DataSet(symbol=self.symbol, frequency=self.frequency, bars=tuple(filtered))

    def start(self) -> datetime | None:
        return self.bars[0].datetime if self.bars else None

    def end(self) -> datetime | None:
        return self.bars[-1].datetime if self.bars else None
