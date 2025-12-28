from __future__ import annotations

from dataclasses import dataclass

from modules.data_sources.models import Bar

from .base import Strategy


@dataclass(frozen=True)
class MovingAverageCrossStrategy(Strategy):
    short_window: int = 5
    long_window: int = 20
    position_size: float = 1.0

    def on_bar(self, bar: Bar, history: list[Bar]) -> float:
        if len(history) < self.long_window:
            return 0.0
        closes = [item.close for item in history]
        short_ma = sum(closes[-self.short_window :]) / self.short_window
        long_ma = sum(closes[-self.long_window :]) / self.long_window
        return self.position_size if short_ma > long_ma else 0.0
