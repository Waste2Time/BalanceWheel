from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple


@dataclass(frozen=True)
class EquityPoint:
    datetime: datetime
    equity: float


@dataclass(frozen=True)
class Trade:
    datetime: datetime
    price: float
    size: float


@dataclass(frozen=True)
class ReturnPoint:
    datetime: datetime
    return_pct: float


@dataclass(frozen=True)
class BacktestResult:
    equity_curve: tuple[EquityPoint, ...]
    trades: tuple[Trade, ...]
    performance_metrics: dict[str, float]
    daily_returns: tuple[ReturnPoint, ...] = tuple()
