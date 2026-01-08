"""Persistence for normalized data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


class CsvRepository:
    """Save normalized data to CSV files."""

    def __init__(self, root: str | Path = "data") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, symbol: str, asset_type: str, data: pd.DataFrame) -> Path:
        filename = f"{asset_type}_{symbol}.csv"
        path = self.root / filename
        data.to_csv(path, index=False)
        return path
