"""Data service for fetching and saving market data."""

from __future__ import annotations

from typing import Mapping

import pandas as pd

from balancewheel.data.interfaces import DataProvider, DataRequest
from balancewheel.data.normalize import normalize_ohlcv
from balancewheel.data.repository import CsvRepository, build_meta
from balancewheel.data.validation import validate_ohlcv


class DataService:
    """Coordinate data fetching and persistence."""

    def __init__(self, providers: Mapping[str, DataProvider], repository: CsvRepository) -> None:
        self.providers = providers
        self.repository = repository

    def fetch_and_save(self, request: DataRequest, provider_name: str) -> pd.DataFrame:
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")

        normalized = self._fetch_with_cross_validation(request, provider_name)
        path = self.repository.save(request.symbol, request.asset_type, normalized)
        meta = build_meta(
            symbol=request.symbol,
            path=path,
            source=provider_name,
            adjust=request.adjust,
            start=request.start,
            end=request.end,
            data=normalized,
        )
        self.repository.write_meta(record=meta, batch=meta)
        return normalized

    def _fetch_with_cross_validation(
        self, request: DataRequest, primary_provider: str
    ) -> pd.DataFrame:
        datasets: dict[str, pd.DataFrame] = {}
        for name, provider in self.providers.items():
            raw = provider.fetch_daily_ohlcv(request)
            normalized = normalize_ohlcv(raw)
            normalized = normalized.sort_values("datetime").reset_index(drop=True)
            validate_ohlcv(normalized)
            datasets[name] = normalized

        primary = datasets[primary_provider]
        for name, dataset in datasets.items():
            if name == primary_provider:
                continue
            if not primary.equals(dataset):
                raise ValueError(f"Data mismatch between {primary_provider} and {name}")
        return primary
