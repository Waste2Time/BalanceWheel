from __future__ import annotations

import abc
from typing import Dict, Optional

import pandas as pd

from modules.strategies.base import Strategy
from .result import BacktestResult


class BacktestEngine(abc.ABC):
    @abc.abstractmethod
    def run(
        self,
        strategy: Strategy,
        data: pd.DataFrame,
        config: Optional[Dict[str, object]] = None,
    ) -> BacktestResult:
        """Execute backtest and return standardized result."""
