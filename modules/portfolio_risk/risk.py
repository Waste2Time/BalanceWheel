from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskLimits:
    max_drawdown: float = 0.2
    max_volatility: float | None = None


def check_drawdown(drawdown: float, limits: RiskLimits) -> bool:
    return drawdown <= limits.max_drawdown
