"""Data service for fetching and saving market data."""

from __future__ import annotations

from typing import Mapping

import pandas as pd

from balancewheel.data.interfaces import DataProvider, DataRequest
from balancewheel.data.normalize import normalize_ohlcv
from balancewheel.data.repository import CsvRepository


class DataService:
    """Coordinate data fetching and persistence."""

    def __init__(self, providers: Mapping[str, DataProvider], repository: CsvRepository) -> None:
        self.providers = providers
        self.repository = repository

    def fetch_and_save(self, request: DataRequest, provider_name: str) -> pd.DataFrame:
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")

        raw = self.providers[provider_name].fetch_daily_ohlcv(request)
        normalized = normalize_ohlcv(raw)
        self.repository.save(request.symbol, request.asset_type, normalized)
        return normalized
