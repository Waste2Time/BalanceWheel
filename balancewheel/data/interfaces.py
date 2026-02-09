"""Interfaces for data providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, Literal, Mapping

import pandas as pd

from balancewheel.data.model import Bar

AssetType = Literal["stock", "etf", "index"]
AdjustType = Literal["none", "qfq", "hfq"]


@dataclass(frozen=True)
class DataRequest:
    symbol: str
    asset_type: AssetType
    start: str
    end: str
    adjust: AdjustType = "none"


class DataProvider(ABC):
    """Abstract base class for market data providers."""

    name: str

    @abstractmethod
    def fetch_daily_ohlcv(self, request: DataRequest) -> pd.DataFrame:
        """Return daily OHLCV data with provider-specific columns."""

    def iter_bars(
        self, *args: object, **kwargs: object
    ) -> Iterable[tuple[Any, Bar | Mapping[str, Bar]]]:
        """Yield (datetime, bars) pairs for engine consumption."""

        raise NotImplementedError
