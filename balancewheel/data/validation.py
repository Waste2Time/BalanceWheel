"""Validation utilities for normalized OHLCV data."""

from __future__ import annotations

import pandas as pd


def validate_ohlcv(data: pd.DataFrame) -> None:
    """Validate normalized OHLCV data for basic consistency."""
    if data.empty:
        raise ValueError("DataFrame is empty")

    if data["datetime"].isna().any():
        raise ValueError("Datetime column contains missing values")

    if not data["datetime"].is_monotonic_increasing:
        raise ValueError("Datetime column must be strictly increasing")

    if data["datetime"].duplicated().any():
        raise ValueError("Datetime column contains duplicate values")

    invalid_high = data["high"] < data[["open", "close"]].max(axis=1)
    invalid_low = data["low"] > data[["open", "close"]].min(axis=1)
    invalid_range = data["high"] < data["low"]
    if (invalid_high | invalid_low | invalid_range).any():
        raise ValueError("Invalid OHLC values detected")
