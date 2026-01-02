from __future__ import annotations

from dataclasses import dataclass


def _normalize(weights: dict[str, float]) -> dict[str, float]:
    total = sum(weights.values())
    if total == 0:
        return {symbol: 0.0 for symbol in weights}
    return {symbol: weight / total for symbol, weight in weights.items()}


@dataclass(frozen=True)
class PortfolioStrategy:
    target_weights: dict[str, float]

    def weights(self) -> dict[str, float]:
        return _normalize(self.target_weights)


@dataclass(frozen=True)
class EqualWeightPortfolioStrategy(PortfolioStrategy):
    symbols: tuple[str, ...] = tuple()

    def __init__(self, symbols: tuple[str, ...]):
        super().__init__(target_weights={symbol: 1.0 for symbol in symbols})
        object.__setattr__(self, "symbols", symbols)
