"""Data model definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Bar:
    datetime: Any
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float
    amplitude: float
    change_pct: float
    change: float
    turnover: float
