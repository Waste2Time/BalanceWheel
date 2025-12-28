from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PortfolioStrategy:
    target_weights: dict[str, float]

    def weights(self) -> dict[str, float]:
        total = sum(self.target_weights.values())
        if total == 0:
            return {symbol: 0.0 for symbol in self.target_weights}
        return {symbol: weight / total for symbol, weight in self.target_weights.items()}
