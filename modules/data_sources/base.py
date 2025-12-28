from __future__ import annotations

import abc
from datetime import date
from typing import Optional

import pandas as pd


class DataSource(abc.ABC):
    """Abstract data source returning standardized OHLCV data."""

    @abc.abstractmethod
    def fetch(
        self, symbol: str, start: Optional[date] = None, end: Optional[date] = None
    ) -> pd.DataFrame:
        """Return a DataFrame indexed by date with columns: open, high, low, close, volume."""


class DataSourceError(Exception):
    """Raised when a data source fails to produce usable data."""


def ensure_ohlcv_columns(df: pd.DataFrame) -> pd.DataFrame:
    expected = ["open", "high", "low", "close", "volume"]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise DataSourceError(f"Missing required columns: {missing}")
    return df[expected]
