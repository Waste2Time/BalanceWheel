"""Normalize provider data to standard schema."""

from __future__ import annotations

import pandas as pd

from balancewheel.data.schema import STANDARD_COLUMNS

COLUMN_ALIASES = {
    "date": "datetime",
    "时间": "datetime",
    "日期": "datetime",
    "open": "open",
    "开盘": "open",
    "high": "high",
    "最高": "high",
    "low": "low",
    "最低": "low",
    "close": "close",
    "收盘": "close",
    "volume": "volume",
    "成交量": "volume",
    "amount": "amount",
    "成交额": "amount",
}


def normalize_ohlcv(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize OHLCV data to standard columns."""
    renamed = {
        column: COLUMN_ALIASES.get(column, column)
        for column in frame.columns
        if column in COLUMN_ALIASES
    }
    data = frame.rename(columns=renamed)

    for column in STANDARD_COLUMNS:
        if column not in data.columns:
            data[column] = 0

    data = data[STANDARD_COLUMNS]
    data["datetime"] = pd.to_datetime(data["datetime"])
    numeric_cols = [col for col in STANDARD_COLUMNS if col != "datetime"]
    data[numeric_cols] = data[numeric_cols].apply(pd.to_numeric, errors="coerce")
    data = apply_missing_strategy(data)
    return data


def apply_missing_strategy(data: pd.DataFrame) -> pd.DataFrame:
    """Apply fixed missing value strategy."""
    data = data.copy()
    price_cols = ["open", "high", "low", "close"]
    data[price_cols] = data[price_cols].ffill()
    data[price_cols] = data[price_cols].fillna(0)
    data[["volume", "amount"]] = data[["volume", "amount"]].fillna(0)
    return data
