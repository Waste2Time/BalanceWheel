from __future__ import annotations

from typing import Dict, List

import pandas as pd


REQUIRED_COLUMNS = ["open", "high", "low", "close", "volume"]


def validate_ohlcv(df: pd.DataFrame) -> Dict[str, object]:
    issues: List[str] = []
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        issues.append(f"missing columns: {missing}")
    if not df.index.is_monotonic_increasing:
        issues.append("index not sorted; sorted ascending")
        df.sort_index(inplace=True)
    if df.index.has_duplicates:
        issues.append("duplicate index; dropping duplicates")
        df = df[~df.index.duplicated(keep="first")]
    if df.isna().any().any():
        issues.append("data contains NaN; forward/backward filled")
        df.fillna(method="ffill", inplace=True)
        df.fillna(method="bfill", inplace=True)
    return {"data": df, "issues": issues}


def compare_sources(primary: pd.DataFrame, secondary: pd.DataFrame) -> Dict[str, object]:
    joined = primary.join(secondary, lsuffix="_p", rsuffix="_s", how="inner")
    diffs = (joined[[f"{col}_p" for col in REQUIRED_COLUMNS]].values - joined[[f"{col}_s" for col in REQUIRED_COLUMNS]].values)
    max_abs_diff = abs(diffs).max()
    return {"rows_compared": len(joined), "max_abs_diff": max_abs_diff}
