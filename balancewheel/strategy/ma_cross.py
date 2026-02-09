"""Moving average cross strategy."""

from __future__ import annotations

from statistics import fmean
from typing import Iterable, Sequence

from balancewheel.engine.strategy_adapter import Signal
from balancewheel.strategy.context import StrategyContext
from balancewheel.strategy.lifecycle import BaseStrategy


class MovingAverageCrossStrategy(BaseStrategy):
    """Simple 20/60 day moving average cross strategy."""

    short_window: int = 20
    long_window: int = 60

    def on_bar(self, context: StrategyContext) -> Signal:
        closes = self._extract_closes(context)
        if len(closes) < self.long_window + 1:
            return Signal.HOLD

        short_now = fmean(closes[-self.short_window :])
        long_now = fmean(closes[-self.long_window :])
        short_prev = fmean(closes[-self.short_window - 1 : -1])
        long_prev = fmean(closes[-self.long_window - 1 : -1])

        if short_prev <= long_prev and short_now > long_now:
            return Signal.BUY
        if short_prev >= long_prev and short_now < long_now:
            return Signal.SELL
        return Signal.HOLD

    def _extract_closes(self, context: StrategyContext) -> Sequence[float]:
        history = context.history
        closes: Iterable[float] | None = None
        if isinstance(history, dict):
            closes = history.get("close")
        if closes is None:
            return []
        return list(closes)
