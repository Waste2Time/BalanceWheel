from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RotationSignal:
    symbol: str
    score: float


@dataclass(frozen=True)
class RotationStrategy:
    lookback_window: int = 20
    top_k: int = 1

    def rank(self, price_series: dict[str, list[float]]) -> list[RotationSignal]:
        signals: list[RotationSignal] = []
        for symbol, prices in price_series.items():
            if len(prices) < self.lookback_window:
                continue
            start = prices[-self.lookback_window]
            end = prices[-1]
            score = (end - start) / start if start else 0.0
            signals.append(RotationSignal(symbol=symbol, score=score))
        return sorted(signals, key=lambda item: item.score, reverse=True)[: self.top_k]
