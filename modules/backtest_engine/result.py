from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pandas as pd


@dataclass
class Trade:
    entry_date: pd.Timestamp
    entry_price: float
    exit_date: Optional[pd.Timestamp]
    exit_price: Optional[float]
    quantity: float
    pnl: float


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    metrics: Dict[str, float]
    trades: List[Trade] = field(default_factory=list)
    signals: Optional[pd.DataFrame] = None
