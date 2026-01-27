"""Data service for fetching and saving market data."""

from __future__ import annotations

from typing import Mapping

import pandas as pd
import numpy as np

from balancewheel.data.interfaces import DataProvider, DataRequest
from balancewheel.data.normalize import normalize_ohlcv
from balancewheel.data.providers.akshare_provider import AkshareEtfSinaProvider
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
        data_to_save = normalized
        if provider_name in {"akshare", "akshare_sina"}:
            data_to_save = normalized.copy()
            data_to_save["volume"] = data_to_save["volume"] * 100
        path = self.repository.save(request.symbol, request.asset_type, data_to_save)
        meta = build_meta(
            symbol=request.symbol,
            path=path,
            source=provider_name,
            adjust=request.adjust,
            start=request.start,
            end=request.end,
            data=data_to_save,
        )
        self.repository.write_meta(record=meta, batch=meta)
        return normalized

    def _fetch_with_cross_validation(
        self, request: DataRequest, primary_provider: str
    ) -> pd.DataFrame:
        datasets: dict[str, pd.DataFrame] = {}
        providers = dict(self.providers)

        if request.asset_type == "etf":
            providers.pop("baostock", None)
            providers["akshare_sina"] = AkshareEtfSinaProvider()

        if primary_provider not in providers:
            raise ValueError(f"Primary provider not available for asset type: {primary_provider}")

        for name, provider in providers.items():
            raw = provider.fetch_daily_ohlcv(request)
            normalized = normalize_ohlcv(raw)
            normalized = normalized.sort_values("datetime").reset_index(drop=True)
            if request.asset_type == "etf" and name == "akshare_sina":
                start = pd.to_datetime(request.start)
                end = pd.to_datetime(request.end)
                normalized = normalized[
                    (normalized["datetime"] >= start) & (normalized["datetime"] <= end)
                ].reset_index(drop=True)
            validate_ohlcv(normalized)
            datasets[name] = normalized

        primary = datasets[primary_provider]
        mismatches: list[str] = []
        compare_columns = ["datetime", "open", "high", "low", "close", "volume"]

        def prepare_for_compare(provider_name: str, data: pd.DataFrame) -> pd.DataFrame:
            subset = data[compare_columns].copy()
            if provider_name == "akshare_sina":
                subset["volume"] = subset["volume"] / 100
                subset["volume"] = np.floor(subset["volume"] + 0.5)
            if request.asset_type == "stock" and provider_name == "baostock":
                subset["volume"] = subset["volume"] / 100
                subset["volume"] = np.floor(subset["volume"] + 0.5)
            return subset

        primary_compare = prepare_for_compare(primary_provider, primary)
        for name, dataset in datasets.items():
            if name == primary_provider:
                continue

            other_compare = prepare_for_compare(name, dataset)
            primary_len = len(primary_compare)
            other_len = len(other_compare)
            min_len = min(primary_len, other_len)
            if primary_len != other_len:
                mismatches.append(
                    f"Length mismatch between {primary_provider} ({primary_len}) and {name} ({other_len})"
                )

            for idx in range(min_len):
                primary_row = primary_compare.iloc[idx]
                other_row = other_compare.iloc[idx]
                diff_cols = []
                for column in compare_columns:
                    primary_value = primary_row[column]
                    other_value = other_row[column]
                    if pd.isna(primary_value) and pd.isna(other_value):
                        continue
                    if primary_value != other_value:
                        diff_cols.append(
                            f"{column}: {primary_value} != {other_value}"
                        )
                if diff_cols:
                    row_number = idx + 1
                    date_value = primary_row["datetime"]
                    mismatches.append(
                        f"Row {row_number} ({date_value}): {name} mismatch -> {', '.join(diff_cols)}"
                    )

            if other_len > min_len:
                for idx in range(min_len, other_len):
                    row_number = idx + 1
                    date_value = other_compare.iloc[idx]["datetime"]
                    mismatches.append(
                        f"Row {row_number} ({date_value}): {primary_provider} missing row"
                    )
            elif primary_len > min_len:
                for idx in range(min_len, primary_len):
                    row_number = idx + 1
                    date_value = primary_compare.iloc[idx]["datetime"]
                    mismatches.append(
                        f"Row {row_number} ({date_value}): {name} missing row"
                    )

        if mismatches:
            detail = "\n".join(mismatches)
            raise ValueError(f"Data mismatch detected:\n{detail}")

        return primary
